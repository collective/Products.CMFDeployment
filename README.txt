CMFDeployment

  Introduction

    This tool allows for static deployment of a CMF
    site to multiple target systems akin to the deployment
    features of advanced commerical CMS systems like interwoven 
    or vignette.

  Features

    - Allows for custom skins for deployment separate then
      content management interface.

    - allows for business logic to filter deployed content
      using TALES expressions and Python Scripts

    - Pluggable Deployment Pipelines (Incremental, Full)

    - Pluggable Deployment Protocols, (currently RsyncSSH)

    - retraction of deployed content (using RsyncSSH protocol)

    - Deployment to multiple servers

    - Merging of DirectoryView (skin) resources into 
      merged content.

    - Provides for Mime and Extension mapping to content
  
    - Provides for configurable URI Resolving of internal links 
      within rendered content.

    - extensive statistics gathering and logging frameworks

    - and many more.

  Changes Summary 

    The ChangeLog has more detailed information.

    Since Beta1

    - Comprehensive Configuration Guide
    
    - A sample policy, thats suitable for deploying static copies of
      a basic plone site.

    - Memory optimization

    - Histories now save statistics and Logs from policy execution

    - Lots of fixes to the uri resolver, with a suite of unit tests

    - Better support for composite content types

    - More powerful filtering capabilities

  Todo Before 1.0

    - testing

    - integrate configuration guide into online help 

  Installation

    Developed and  Tested on Linux (2.4), Solaris 9, Mac OS X (Jaguar)
    with Python 2.1.3, Zope 2.5.1 and CMF1.3

    - Decompress distribution file and move to Products
      directory. 

    - restart zope

    - in the root of the cmf site, add an external method::

      Id: install_deployment_tool
      Module: CMFDeployment.Install
      Function: install

    - click on the test tab to complete installation

    Debian users will need to install the pyxml package. 

  Configuration

    The use of this tool requires configuration of several
    sections, outlined below. further documentation can 
    be found in the docs directory.

  Identification

    Identifies Content that should be deployed. The Portal Catalog
    is used as a content source, TALES Filters and Python Script
    Filters can be used to filter the available
    content set, and restrict what content objects will be 
    deployed.

  Organization
    
    Organizes the content in a target directory structure. The default
    structure and organization implementation, utilizes the existing
    cmf structure, although it does allow for mounting from a non 
    portal root folder. 

  Mastering

   The process of rendering/cooking the content.

   - skin selection

   - mime mapping configuration for content

   - render method selection for content

  URIS Link Normalization

    During the mastering process the rendered view of content
    has extensions attached, and intra object references in
    rendered content need to be updated, as well as target url
    host information.  

  Directory View (skin) Merging

  Skins .. Directory Views

    certain resources of directory views often need to be deployed
    alongside content. 

  Deployment

    The actual deployment of content to the target server.
 
    Targets

    Protocols

  Libraries
   
     This Product is distributed with the following
     third party modules which are included here
     under their original license terms, and are 
     distributed here for convience (all such
     files can be found under CMFDeployment/lib)

     - "pexpect":http://pexpect.sf.net - Noah Spurrier (Python License)

     - "policycaller":http://cvs.zope.org/Products/Scheduler/methodcaller.py (ZPL)

     - "linuxproc":http://www.zope.org/Members/mcdonc (ZPL)

     - "LockFile":http://www.list.org (GPL)

  Development Info
  
    - "General Project Info and Wiki":http://projects.objectrealms.net/projects/cmfdeployment

    - "Users Mailing List":https://lists.objectrealms.net/mailman/listinfo/cmfdeployment
    
    - "Changes Mailing List":https://lists.objectrealms.net/mailman/listinfo/cmfdeployment-changes
    
    - "Project Bug Tracking":http://bugs.objectrealms.net    

  License and Copyright
     
    - @ kapil thangavelu 2002-2004

    - "GPL":http://www.fsf.org

  Credits

    "Kapil Thangavelu":mailto://k_vertigo@objectrealms.net - Author

    "Tahara Yusei":http://timedia.co.jp - Patches for Plone2/CMF 1.4

    "Calvin Hendryx-Parker":http://sixfeetup.com - Deployment Skin, Use Cases, and Sponsoring

    "Gael Le Mignot":http://pilotsystems.net - Plone2.1 support

    "Kai Hänninen":http://mbconcert.fi - Plone 2.1 / Zope 2.8 support

    "Osma Suominen":http://mbconcert.fi - Plone 2.1 / Zope 2.8 support

    "Ken Wasetis":http://contextualcorp.com - Sponsoring, and bug reports

    "Lawrence Rowe":http://objectvibe.com - compatiblity permission patch, and bug reports 

    I'd like to thank alan runyaga for much dicussion
    and feedback on this tool. It has benefited greatly 
    from his insights and wisdom.

    I'd like to thank my employer for allowing
    me to opensource this tool that was developed at
    their cost. Without companies and clients such as 
    them the open source world would be a much poorer 
    place.
