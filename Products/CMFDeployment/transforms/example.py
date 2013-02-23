"""
an example content transform. content transformss are executed over matched
rendered content immediately before storage.

$Id: example.py 940 2005-08-16 07:50:44Z hazmat $
"""

from registry import registerTransform

def example_transform(descriptor, rendered_content, file_path):
    """
    descriptor is a content descriptor object, it offers
    access to the context, the deployed content object, and
    various deployment metadata about the object.

    rendered content is a string of the content object in
    rendered form.

    file path, represents the filesystem path that the rendered
    content will be stored at on the *zope server*, not the
    deployment server.

    currently only modifications to the rendered content are
    tracked. changing this is trivial
    """

    # lets change all 'the's to 'The'
    return rendered_content.replace('the', 'The')

# register the transform so we can use it
registerTransform('THE_example', example_transform)
