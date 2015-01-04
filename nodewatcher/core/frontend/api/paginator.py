from django_datastream import test_runner


class Paginator(test_runner.Paginator):
    def page(self):
        # We add count of all objects before filtering (used in dataTables)
        page = super(Paginator, self).page()
        if hasattr(self.objects, '_nonfiltered_count'):
            page['meta']['nonfiltered_count'] = self.objects._nonfiltered_count
        return page
