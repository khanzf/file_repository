from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseNotFound
from django.http import HttpResponseServerError

# You would have to do this in your application
from file_repository.models import Inode
from file_repository.forms import DirectoryForm, FileForm
from file_repository.commands import get_inode, del_inode, create_root, create_file, create_directory

import magic

def index(request):
    context = {}
    return render(request, 'testapp/index.html', context)

def repository(request, filedir):
    directoryform = DirectoryForm
    fileform = FileForm

    i = get_inode(filedir, 'testapp')

    print("The root directory is: %s" % i.get_path())

    if hasattr(i, 'error'):
        if i.error == 404:
            return HttpResponseNotFound('<h1>File or directory not found</h1>')
        elif i.error == 500:
            return HttpResponseServerError('<h1>Internal server error</h1>')

    if request.method == 'POST':
        directoryform = DirectoryForm(request.POST)
        fileform = FileForm(request.POST, request.FILES)
        if directoryform.is_valid():
            create_directory(i,
                             directoryform.cleaned_data['name'])
        elif fileform.is_valid():
            create_file(i,
                        fileform.cleaned_data['content'].name,
                        fileform.cleaned_data['content'])

    if i.is_directory==False:
        file_content = i.content.read()
        content_type = magic.from_buffer(file_content, mime=True).decode()
        response = HttpResponse(content_type=content_type)
        response.write(file_content)
        return response
    elif i.is_directory==True:
        context = {'directorynode':             i,
                   'directoryform':     directoryform,
                   'fileform':          fileform,    
                   'filedir':           filedir if filedir is not None else '/',
                  }

        return render(request, 'testapp/repository.html', context)
