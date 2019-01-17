from jumpscale import j

# declaring list of store data

class farmers:
    def list(self):
        self.capacity = j.clients.threefold_directory.get(interactive=False)
        mylist, response = self.capacity.api.ListFarmers()
        self.farm_names = []
        for obj in mylist:
            self.farm_names.append(obj.name)
        return self.farm_names

    def check_farm_existing (self,myfarm):
        self.myfarm = myfarm
        for f in self.farm_names:
            if f == self.myfarm:
                print ('the farm name {} is exist ....'.format(self.myfarm))
            #else:
            #    print ('the farm name {} does not exist on our grid, check may no node are added to it '.format(self.myfarm))
