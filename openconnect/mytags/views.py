from django.template import RequestContext
from django.shortcuts import *
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from tagging.models import Tag, TaggedItem
from tagging.utils import edit_string_for_tags
from contacts.models import Contact
from mytags.forms import RenameTag


@login_required
def manage(request):
    tags = Tag.objects.all()
    return render_to_response('contacts/managetags.html', context_instance=RequestContext(request, {'tags':tags}))


@login_required
def rename(request, tagname):
    if request.method == "POST":
	print "what"
        #oldtag = Tag.objects.get(name__exact=tagname)
        #contacts = TaggedItem.objects.get_by_model(Contact, oldtag)
        #for c in contacts:
        #    newtagstr = c.tag_list.replace(oldtag.name, request.POST['name'])
        #    c.tag_list = newtagstr
        #    c.save()
        #oldtag.name = request.POST['name']
	#oldtag.save()
        form = RenameTag(request.POST, instance=Tag.objects.get(name__exact=tagname))   
        if form.is_valid():
            form.save()
	else:
	    return render_to_response('contacts/renametag.html', context_instance=RequestContext(request, {'form':form, 'tagname':tagname}))

        return HttpResponseRedirect('/tagging/manage/')
    else:
        form = RenameTag(instance=Tag.objects.get(name__exact=tagname))
    return render_to_response('contacts/renametag.html', context_instance=RequestContext(request, {'form':form, 'tagname':tagname}))


@login_required
def remove(request, tagname):
    if request.method == "POST":
        if request.POST['submit'] == "Yes, delete this tag":
            # delete the tag and all references
            t = Tag.objects.get(name__exact=tagname)
            taggedcontacts = TaggedItem.objects.get_by_model(Contact, t)
            for c in taggedcontacts:
                newtags = c.tag_list.replace(tagname, "")
                c.tag_list = newtags
                c.save()
            t.delete()
            return HttpResponseRedirect('/tagging/manage/')
        else:
            return HttpResponseRedirect('/tagging/manage/')
    else:
        t = Tag.objects.get(name__exact=tagname)
        return render_to_response('contacts/deletetag_confirm.html', context_instance=RequestContext(request, {'tag': t}))
