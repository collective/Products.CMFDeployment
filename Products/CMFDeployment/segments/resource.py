from core import PipeSegment


class SiteResourceDeploy( PipeSegment ):
    """
    """

    def __init__(self, incremental=False):
        self.incremental = incremental

    def process( self, pipe, content ):
        resources = pipe.services["SiteResources"]
        resolver = pipe.services['ContentResolver']
        store = pipe.services["ContentStorage"]


        if self.incremental and pipe.variables['LastDeployTime'] is not None:
            dtime = pipe.variables['LastDeployTime']
        else:
            dtime = None
            
        contents = list( resources.getContent(dtime) )
            
        for rd in contents:
            resolver.addResource( rd )


        for rd in contents:
            resources.cook( rd )
            resolver.resolve( rd )
            store.add( pipe, rd )

