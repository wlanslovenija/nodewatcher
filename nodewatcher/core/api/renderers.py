from drf_ujson import renderers


class JSONRenderer(renderers.UJSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if renderer_context.get('indent', None):
            return super(renderers.UJSONRenderer, self).render(data, accepted_media_type, renderer_context)
        else:
            return super(JSONRenderer, self).render(data, accepted_media_type, renderer_context)
