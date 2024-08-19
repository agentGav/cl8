#!/usr/bin/env python

# this is a quick check to see that files can upload to the expected location
# in object storage. This exercises the code to upload a file to the default
# location specified default storage.
# This allows you to see where that would be in object storage for example,
# check the upload path is what you expect


from django.core.files.storage import default_storage

file = default_storage.open("storage_test", "w")
file.write("test storage contents")
file.close()

assert default_storage.exists("storage_test")
