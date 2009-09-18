from haystack.views import SearchView

class CoralSearchView(SearchView):
	def __name__(self):
		return "CoralSearchView"

	def extra_context(self):
		extra = super(CoralSearchView, self).extra_context()

		extra['tab'] = 'search'
		extra['q'] = self.request.GET.get('q', None)

		return extra
