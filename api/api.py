from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import Http404, JsonResponse

from rest_framework import (
    routers,
    serializers,
    views,
    viewsets,
    response,
    decorators,
    filters,
    status,
    permissions
)

from .models import Group, Permission, Hub
from .filters import IsOwnerFilterBackend
from .helpers import (can_become, kong_login)
from multiguru.guru import get_headers

import requests

class HubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hub
        fields = '__all__'

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    filter_backends = (
        filters.SearchFilter,
        filters.OrderingFilter,
        IsOwnerFilterBackend)

    @decorators.list_route(methods=['get'])
    def expand(self, request):
        '''Fetch profile for each member of the group'''
        groups = Group.objects.filter(members__contains = [request.user.id])
        response = []
        for group in groups:
            group_data = GroupSerializer(group).data

            member_data = []
            for member_id in group.members:
                config = settings.PROXIED_APIS.get(settings.APPOINTMENTGURU_NAME)
                path = config.get('profile').format(member_id)
                url = '{}{}'.format(config.get('base_url'), path)
                headers = get_headers(request.user.id)
                result = requests.get(url, headers=headers)
                member_data.append(result.json())
            group_data.update({'data': member_data})
            response.append(group_data)

        return JsonResponse(response, safe=False)


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer

class HubViewSet(viewsets.ModelViewSet):
    queryset = Hub.objects.all()
    serializer_class = HubSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self):
        queryset = self.get_queryset()
        pk = self.kwargs.get('pk')
        try:
            int(pk)
            obj = queryset.get(id=pk)
        except ValueError:
            obj = get_object_or_404(queryset, slug=pk)
        return obj


class BecomeViewSet(viewsets.ViewSet):

    def create(self, request):
        become_id = request.data.get('become_id', None)
        logged_in_id = request.user.id

        if can_become(become_id, logged_in_id):
            # todo: unhardcode this:
            response = kong_login(become_id)
            return JsonResponse(response)
        else:
            response = { "errors": [ 'Authentication failed' ] }
            return JsonResponse(response, status=status.HTTP_403_FORBIDDEN)

class ProxyViewSet(viewsets.ViewSet):
    '''Simple class that proxys requests upstream according to the user's permissions'''

    async def __get(self, url, headers={}, params={}, data={}):
        print('fetching: {}'.format(url))
        result = requests.get(
                    url,
                    headers=headers,
                    params=params,
                    data=data)
        print('got: {}'.format(result.url))
        return result

    def __get_config(self, request, api):
        group_id = request.GET.get('group')
        resource = request.GET.get('resource')

        group = get_object_or_404(Group, id=group_id)
        api_config = settings.PROXIED_APIS.get(api)

        not_a_member_of_this_group = str(request.user.id) in group.members
        if not not_a_member_of_this_group: raise Http404

        downstream_params = {key.replace('param.',''): val for (key, val) in request.GET.items() if key.startswith('param.')}

        return (group, resource, api_config, downstream_params)

    def list(self, request):
        '''
        /:group/:lookup/?params=
            e.g.:
        /referrrals/appointments/?params=practitioner_id=..
        or
        /some-practice/appointmets/?date=..
        '''
        group, resource, api_config, downstream_params = self.__get_config(request, settings.APPOINTMENTGURU_NAME)
        results = {}
        for user_id in group.members:
            headers = get_headers(user_id)
            base = api_config.get('base_url')
            path = api_config.get(resource).format(user_id)
            url = '{}{}'.format(base, path)

            result = requests.get(url, headers=headers, params=downstream_params)
            results[user_id] = result.json()
        # ioloop = asyncio.get_event_loop()
        # for user_id in group.members:
        #     headers = get_headers(user_id)
        #     url = request_data.get('upstream').format(user_id)
        #     # result = requests.get(url, headers=headers)
        #     tasks.append(ioloop.create_task(self.__get(url, headers=headers)))

        # wait_tasks = asyncio.wait(tasks)
        # ioloop.run_until_complete(wait_tasks)
        # ioloop.close()

        return response.Response(results)

    def retrieve(self, request, pk):
        pass

    def create(self, request):
        '''
        Proxy POST requests
        /proxy/?group=..&resource=..
        --data={
            ...
        }

        => /upstream --data = data.data
        '''
        group_id = request.GET.get('group')
        resource = request.GET.get('resource')
        practitioner_id = request.data.get('practitioner')

        api_config = settings.PROXIED_APIS.get(settings.APPOINTMENTGURU_NAME)
        url = '{}{}'.format(api_config.get('base_url'), api_config.get(resource))
        data = request.data
        result = requests.post(url, data, headers=get_headers(practitioner_id))
        return response.Response(result.json())


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'become', BecomeViewSet, base_name='become')
router.register(r'groups', GroupViewSet)
router.register(r'hubs', HubViewSet)
router.register(r'permissions', PermissionViewSet)
router.register(r'proxy', ProxyViewSet, base_name='proxy')
