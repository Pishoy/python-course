import time



class checker():

    def __init__(self,myfarm):
        self.myfarm = myfarm
        self.capacity = j.clients.threefold_directory.get(interactive=False)
        try:
            self.capacity.api.GetFarmer(self.myfarm)
            self.resp = self.capacity.api.ListCapacity(query_params={'farmer': self.myfarm})[1]
            self.nodes = self.resp.json()

        except:
             self.logger = j.logger.get('checking farm existing')
             self.logger.error('farm name {} does not exist please check your farm name or check capacity website '.format(self.myfarm))
    def node_list(self,offline=False):
        self.logger.get('check nodes for farm')
        self.logger.info("fetching nodes list")
        self.timelimit = 7 * 86400 # 7days
        timenow = time.time()
        rnodes = []
        for node in self.nodes:
            if not offline: # if user does not give offline flag so he need the node that has last updated of 7 days ago
                if not node['updated']: ## reject the ndoes that does not have updated flag
                    continue
                if node['updated'] > timenow - self.timelimit:
                    continue
                rnodes.append(node)
        return rnodes

