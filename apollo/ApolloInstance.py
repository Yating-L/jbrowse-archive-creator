#!/usr/bin/env python
import json
import logging
from util import subtools

class ApolloInstance(object):
    def __init__(self, apollo_host):
        self.apollo_host = apollo_host
        self.logger = logging.getLogger(__name__)

    def getHost(self):
        return self.apollo_host

    def createApolloUser(self, apollo_user, admin=None):
        p = subtools.arrow_create_user(apollo_user.user_email, apollo_user.firstname, apollo_user.lastname, apollo_user.password, admin) 
        user_info = json.loads(p)
        user_id = user_info.get('userId')
        if not user_id:
            self.logger.debug("Cannot create new user: %s; The user may already exist", apollo_user.user_email)
            user_id = subtools.arrow_get_users(apollo_user.user_email)
        self.logger.debug("Got user_id for new or existing user: user_id = %s", str(user_id))
        return user_id   

    def grantPermission(self, user_id, organism_id, **user_permissions):
        subtools.arrow_update_organism_permissions(user_id, organism_id, **user_permissions)
        self.logger.debug("Grant user %s permissions to organism %s, permissions = %s", str(user_id), str(organism_id), ','.join(user_permissions))

    def addOrganism(self, organism_name, organism_dir):
        p = subtools.arrow_add_organism(organism_name, organism_dir)
        organism = json.loads(p)
        organism_id = organism['id']
        self.logger.debug("Added new organism to Apollo instance, %s", p)
        return organism_id

    def loadHubToApollo(self, apollo_user, organism_name, organism_dir, admin_user=False, **user_permissions):
        user_id = self.createApolloUser(apollo_user, admin_user)
        organism_id = self.addOrganism(organism_name, organism_dir)
        self.grantPermission(user_id, organism_id, **user_permissions)
        self.logger.debug("Successfully load the hub to Apollo")