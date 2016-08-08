import requests
import json


class APICall():
    """
    Description:

    """
    def api_for_each_commit(self,commit_id):
        """
        Description:
                    This function calling the git api too each commit id and returning commit information 
        """
        commit_response = requests.get('https://api.github.com/repos/devendraratnam747/DelhiProject/commits/%s'%(commit_id))
        return  commit_response

    def api_for_all_repository(self,organization_name):
        """
        Description :
                listing_down all repos in organization 
        args:
            organization_name : name of organiation example: Delhivery

            
        """
        response = requests.get("https://api.github.com/orgs/delhivery/repos").json()
        repos_list = []
        for each in response :
            repos_list.push(each.get('full_name'))
 
        return repos_list
