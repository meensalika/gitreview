import requests
import json
import logging

from rest_framework.pagination import (
    LimitOffsetPagination,
    PageNumberPagination,
    )

from rest_framework import exceptions
from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from django.http import Http404
from django.conf import settings
from rest_framework import generics
from rest_framework import filters
from pagination import CommentLimitOffsetPagination

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView


from gitapp.services.gitapi import *
from gitapp.models import  GITComments, GITCommits
from gitapp.services.api import APICall
from gitapp.serializers import GITCommentsSerializer, GITCommitsSerializer
from gitapp.apiviews.utils import create_commit, create_comment


class GITApiCall(ViewSet):
    """
    Description :
        Service api 
        Api request method :GET
    """
    def fetch_git_comments(self, *args, **kwargs):
        """
        Description:
            Method to fetch all comments or reviews from github of a specified repository
        args:

        """       
        comments_list = []
        repository_name = settings.REPOSITORY
        comment_response = GitAPIServices().get_comments(repository_name)       
        for each in comment_response:
            comments = GITComments.objects.filter(
                git_comment_id=each.get('id'))
            if not comments:
                commit_response = APICall().api_for_each_commit(
                    each.get('commit_id')).json()
                commit_obj = create_commit(commit_response, repository_name)
                create_comment(each, commit_obj, commit_obj, repository_name)
        return Response({"success": True})


class CommentForUser(generics.ListAPIView):
    #import ipdb;ipdb.set_trace()
    """
    Description:
    Enter user name and get list of comment of the users
    args:
    username: github username,from_date ,to_date,repository:user

    """
    serializer_class = GITCommentsSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filter_fields = ['comment_message','rating']
    pagination_class = CommentLimitOffsetPagination

    def get_queryset(self):
        #import ipdb;ipdb.set_trace()
        username = self.kwargs.get('username')
        #mport ipdb;ipdb.set_trace()
        filter_dict = {'commit__committed_by__username':username}
        #filter_dict ={}
        if username is not None:
            if self.request.query_params.get('from_date'):
                filter_dict.update({
                'created_at__gte': self.request.query_params.get('from_date')})
            if self.request.query_params.get('to_date'):
                filter_dict.update({
                'created_at__lte': self.request.query_params.get('to_date')})
            if self.request.query_params.get('repository'):
                filter_dict.update({
                'repository': self.request.query_params.get('repository')})
            try:
                user = User.objects.get(username=username)
                queryset = GITComments.objects.filter(**filter_dict)
            except User.DoesNotExist:
                    raise exceptions.NotFound(detail="Comment Not Found for user {}".format(username))
        return queryset;



class RepositoryForUser(generics.ListAPIView):
    """
    Descrition:
        api for all repository of entered user
    """

    serializer_class = GITCommitsSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filter_fields = ['repository',]
    #pagination_class = CommentLimitOffsetPagination

    def get_queryset(self):
        """
        Descrition:               
            Return repository name for given username
        args:
            username : github username
        """
        username  = self.kwargs.get('username')
        try:
            User.objects.get(username=username)    
            query_set = GITCommits.objects.filter(committed_by__username=username)        
        except User.DoesNotExist:
            raise exceptions.NotFound(detail=" ")
        return query_set

    def get_paginated_response(self,data):
        """ 
        Descrition:
            overiding get method of ListAPIView and  returning
            a paginated style `Response` object for the given output data.
        """
        repo_list = []
        repository_list = self.get_queryset()
        for each in repository_list:
            repo_list.append(each.repository)

        repo_list = set(repo_list) 
        repo_list = list(repo_list)
       
        assert self.paginator is not None
        return self.paginator.get_paginated_response(repo_list)
