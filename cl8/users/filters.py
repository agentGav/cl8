import django_filters
from cl8.users import models as cl8_models
from taggit import models as taggit_models
from dal import autocomplete

from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank


class ProfileFilter(django_filters.FilterSet):
    bio = django_filters.CharFilter(method="search_fulltext")

    tags = django_filters.ModelMultipleChoiceFilter(
        field_name="tags",
        label="Tags",
        queryset=taggit_models.Tag.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(url="tag-autocomplete"),
        conjoined=True,
    )

    def search_fulltext(self, queryset, field_name, value):
        """
        Override the default search behaviour to use Postgres full text search, to search
        a number of fields simultaneously
        """
        # https://github.com/carltongibson/django-filter/issues/1039
        # https://stackoverflow.com/questions/76397037/django-full-text-search-taggit

        search_query = SearchQuery(value, search_type="websearch")
        search_vector = SearchVector(
            # we want the user's name to be searchable
            "user__name",
            # along with all the text of their bio
            "bio",
            # and the text of all the tags associated with the profile
            "tags__name",
        )

        return (
            queryset.annotate(rank=SearchRank(search_vector, search_query))
            .filter(rank__gt=0)
            .distinct()
            .order_by("-rank")
        )

    class Meta:
        model = cl8_models.Profile
        fields = ["bio"]
