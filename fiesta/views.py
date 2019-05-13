
from rest_framework import status 
from rest_framework.response import Response
from rest_framework.views import APIView

from .utils.datastructures import AttrDict
from .models import WSRestStructureRequestRegistration


class SubmitStructureRequestView(APIView):
    
    def post(self, request, format=None):
        request.body
        data_instance = request.data
        process_context = AttrDict(
            request=request,
            errors=[],
            submission=None,
            refs=None,
            submitted=None,
            stop=False
        )
        data_instance.process(process_context=process_context)
        errors = data_instance._process_context.errors
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(data_instance.to_response(), status=status.HTTP_200_OK)

class StructureView(APIView):

    def get(self, request, resource, agencyID='all', resourceID='all', version='latest'):
        query_params = request.query_params
        for key, value in query_params:
            if key not in ['detail', 'references']:
                return Response(f'Query key {query_key} is not acceptable',
                                status=status.HTTP_406_NOT_ACCEPTABLE)
            if value not in constants.QUERY_PARAMS['structure'][key]:
                return Response(f'Query value {value} for query parameter {key} is not allowed',
                                status=status.HTTP_405_METHOD_NOT_ALLOWED)
            detail = query_params.get('detail', 'full') 
            references = query_params.get('references', 'none') 
        registration = WSRestStructureRequest.objects.create(
            requester=request.user,
            resource=resource,
            agency_id=agencyID,
            resource_id=resourceID,
            version=version,
            detail=detail,
            references=references
        )
        # data_instance = structure.Structure().retrieve(registration)
        # return Response(data_instance, status=status.HTTP_200_OK)
        return Response('SDMX RESTful API not yet available', status=status.HTTP_200_OK)
