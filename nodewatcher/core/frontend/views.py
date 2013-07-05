import json

from django import http, shortcuts, template
from django.contrib.auth import decorators as auth_decorators
from django.core import urlresolvers
from django.db import transaction
from django.utils import safestring

from guardian.shortcuts import assign as assign_permission

from .. import models as core_models
from ..registry import forms as registry_forms

def nodes(request):
    """
    Display a list of all current nodes and their status.
    """

    return shortcuts.render_to_response('nodes/list.html', {
        'nodes' : core_models.Node.objects.regpoint("config").registry_fields(
            name = 'GeneralConfig.name',
            type = 'TypeConfig.type',
            router_id = 'RouterIdConfig.router_id',
            status = 'StatusMonitor.status',
        ).order_by('type', 'router_id')
    }, context_instance = template.RequestContext(request))

@auth_decorators.login_required
def node_new(request):
    """
    Display a form for registering a new node.
    """

    if request.method == 'POST':
        sid = transaction.savepoint()
        try:
            node = core_models.Node()
            node.save()

            actions, partial_config = registry_forms.prepare_forms_for_regpoint_root(
                "node.config",
                request,
                node,
                data = request.POST,
                only_rules = True,
            )
            eval_state = actions['STATE']

            has_errors, dynamic_forms = registry_forms.prepare_forms_for_regpoint_root(
                "node.config",
                request,
                node,
                data = request.POST,
                save = True,
                actions = actions,
                current_config = partial_config,
            )

            if not has_errors:
                assign_permission("change_node", request.user, node)
                assign_permission("remove_node", request.user, node)
                transaction.savepoint_commit(sid)
                return http.HttpResponseRedirect(urlresolvers.reverse("view_node", kwargs={ 'node': node.pk }))
            else:
                transaction.savepoint_rollback(sid)
        except:
            transaction.savepoint_rollback(sid)
            raise
    else:
        dynamic_forms, eval_state = registry_forms.prepare_forms_for_regpoint_root(
            "node.config",
            request,
            None,
            also_rules = True,
        )

    return shortcuts.render_to_response('nodes/new.html', {
        'registry_forms' : dynamic_forms,
        'registry_regpoint' : 'node.config',
        'eval_state' : safestring.mark_safe(json.dumps(eval_state)),
    }, context_instance = template.RequestContext(request))

def node_display(request, node):
    pass

@auth_decorators.login_required
def node_edit(request, node):
    """
    Display a form for registering a new node.
    """

    node = shortcuts.get_object_or_404(core_models.Node, pk = node)
    # XXX needs port to permissions
    #if not node.is_current_owner(request):
    #  raise Http404

    if request.method == 'POST':
        actions, partial_config = registry_forms.prepare_forms_for_regpoint_root(
            "node.config",
            request,
            node,
            data = request.POST,
            only_rules = True,
        )
        eval_state = actions['STATE']

        has_errors, dynamic_forms = registry_forms.prepare_forms_for_regpoint_root(
            "node.config",
            request,
            node,
            data = request.POST,
            save = True,
            actions = actions,
            current_config = partial_config,
        )

        if not has_errors:
            return http.HttpResponseRedirect(urlresolvers.reverse("view_node", kwargs={ 'node': node.pk }))
    else:
        dynamic_forms, eval_state = registry_forms.prepare_forms_for_regpoint_root(
            "node.config",
            request,
            node,
            also_rules = True,
        )

    return shortcuts.render_to_response('nodes/edit.html', {
        'node' : node,
        'registry_forms' : dynamic_forms,
        'registry_root' : node,
        'registry_regpoint' : 'node.config',
        'eval_state' : safestring.mark_safe(json.dumps(eval_state)),
    }, context_instance = template.RequestContext(request))
