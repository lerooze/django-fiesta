# views.py

from django.apps import apps
from django.core.files.base import ContentFile
from rest_framework import status 
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.views import APIView

from ..core import constants
from ..core.serializers.options import (
    ProcessContextOptions, RESTfulQueryContextOptions)
from ..core.serializers.structure import StructureSerializer
from ..core.exceptions import NotImplementedError, ParseSerializeError

from ..permissions import IsAgencyUser

class SubmitRegistrationsRequestView(APIView):
    permission_classes = [IsAgencyUser]

    def post(self, request, format=None):
        log_model = apps.get_model('registry', 'log')
        log = log_model.objects.create(
            user=request.user,
            channel='Registry',
            progress='Submitted',
        )
        log.update_progress('Negotiating Content')
        request.body
        log.update_progress('Parsing')
        try:
            data = request.data
        except (ParseError, ParseSerializeError, NotImplementedError) as exc:
            exceptions_file = ContentFile(exc.detail)
            log.exceptions_file.save(f'EXCEPTIONS_{data.m_header.id}', exceptions_file)
            log.update_progress('Finished') 
            raise exc
        log.update_progress('Processing')
        context = ProcessContextOptions(request, log)
        data.process(context=context)
        outdata = data.to_response()
        if data._context.result.submitted_structure.maintainable_object.ref.agency_id == 'MAIN':
            response_status = status.HTTP_400_BAD_REQUEST
        else:
            response_status = status.HTTP_200_OK
        request_file = ContentFile(request.stream)
        log.request_file.save(f'REQUEST_{data.m_header.id}', request_file)
        response = Response(outdata, status=response_status)
        response_file = ContentFile(response)
        log.response_file.save(f'RESPONSE_{data.m_header.id}', response_file)
        log.update_progress('Finished') 
        return response

class SubmitStructureRequestView(APIView):
    
    def post(self, request, format=None):
        log_model = apps.get_model('registry', 'acquisitionlog')
        log = log_model.objects.create(
            user=request.user,
            channel='Registry',
            progress='Submitted',
        )
        log.update_progress('Negotiating Content')
        request.body
        data = request.data
        log.update_progress('Processing')
        context = ProcessContextOptions(request, log)
        data.process(context=context)
        log.update_progress('Negotiating Media')
        outdata = data.to_response()
        if data._context.result.submitted_structure.maintainable_object.ref.agency_id == 'MAIN':
            response_status = status.HTTP_400_BAD_REQUEST
        else:
            response_status = status.HTTP_200_OK
        acquisition_file = ContentFile(request.stream)
        log.acquisition_file.save(f'Ref_{data.m_header.id}.xml',
                                              acquisition_file)
        log.update_progress('Finished')
        return Response(outdata, status=response_status)

class SDMXRESTfulStructureView(APIView):

    def get(self, request, resource, agencyID='all', resourceID='all',
            version='latest'):
        log_model = apps.get_model('registry', 'querylog')
        log = log_model.objects.create(
            user=request.user,
            channel='RESTful_query',
            progress='Submitted',
        )
        query_model = apps.get_model('registry', 'restfulstructurequery')
        query_params = request.query_params
        for key, value in query_params:
            if key not in ['detail', 'references']:
                return Response(
                    f'Query key {key} is not acceptable',
                    status=status.HTTP_406_NOT_ACCEPTABLE
                )
            if value not in constants.QUERY_PARAMS['structure'][key]:
                return Response(
                    f'Query value {value} for query parameter {key} is not '
                    'allowed',
                    status=status.HTTP_405_METHOD_NOT_ALLOWED
                )
            detail = query_params.get('detail', 'full') 
            references = query_params.get('references', 'none') 
        query = query_model.objects.create(
            log = log,
            resource=resource,
            agency_id=agencyID,
            resource_id=resourceID,
            version=version,
            detail=detail,
            references=references
        )
        log.update_progress('Processing')
        context = RESTfulQueryContextOptions(query)
        data = StructureSerializer().retrieve_restful(context)
        data._query = query 
        log.update_progress('Finished')
        return Response(data, status=status.HTTP_200_OK)

class SDMXRESTfulSchemaView(APIView):

    def get(self, request, context, agencyID, resourceID, version='latest'):

        log_model = apps.get_model('registry', 'querylog')
        log = log_model.objects.create(
            user=request.user,
            channel='RESTful_query',
            progress='Submitted',
        )
        schema_query_model = apps.get_model('registry', 'restfulschemaquery')
        structure_query_model = apps.get_model('registry', 'restfulstructurequery')
        query_params = request.query_params
        for key, value in query_params:
            if key not in ['dimensionAtObservation']:
                return Response(
                    f'Query key {key} is not acceptable',
                    status=status.HTTP_406_NOT_ACCEPTABLE
                )
            if value not in constants.QUERY_PARAMS['schema'][key]:
                return Response(
                    f'Query value {value} for query parameter {key} is not '
                    'allowed',
                    status=status.HTTP_405_METHOD_NOT_ALLOWED
                )
            observation_dimension = query_params.get('dimensionAtObservation', 'TIME_PERIOD') 
        schema_query = schema_query_model.objects.create(
            log = log,
            context=context,
            agency_id=agencyID,
            resource_id=resourceID,
            version=version,
            observation_dimension=observation_dimension
        )
        structure_query = structure_query_model.objects.create(
            log = log,
            resource=context,
            agency_id=agencyID,
            resource_id=resourceID,
            version=version,
            detail='full',
            references='children'
        )
        log.update_progress('Processing')
        context = RESTfulQueryContextOptions(structure_query)
        data = StructureSerializer().retrieve_restful(context)
        data._query = schema_query
        log.update_progress('Finished')
        return Response(data, status=status.HTTP_200_OK)
