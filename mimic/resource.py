"""
Resources for Mimic's core.
"""

import json

from twisted.web.resource import NoResource

from mimic.canned_responses.mimic_presets import get_presets
from mimic.rest.mimicapp import MimicApp
from mimic.rest.auth_api import AuthApi, base_uri_from_request


class MimicRoot(object):
    """
    Klein routes for the root of the mimic URI hierarchy.
    """

    app = MimicApp()

    def __init__(self, core):
        """
        :param mimic.core.MimicCore core: The core object to dispatch routes
            from.
        """
        self.core = core

    @app.route("/", methods=["GET"])
    def help(self, request):
        """
        A helpful greeting message.
        """
        request.responseHeaders.setRawHeaders("content-type", ["text/plain"])
        return ("To get started with Mimic, POST an authentication request to:"
                "\n\n/identity/v2.0/tokens")

    @app.route("/identity", branch=True)
    def get_auth_api(self, request):
        """
        Get the identity ...
        """
        return AuthApi(self.core).app.resource()

    @app.route('/mimic/v1.0/presets', methods=['GET'])
    def get_mimic_presets(self, request):
        """
        Return the preset values for mimic
        """
        request.setResponseCode(200)
        return json.dumps(get_presets)

    @app.route("/service/<string:region_name>/<string:service_id>",
               branch=True)
    def get_service_resource(self, request, region_name, service_id):
        """
        Based on the URL prefix of a region and a service, where the region is
        an identifier (like ORD, DFW, etc) and service is a
        dynamically-generated UUID for a particular plugin, retrieve the
        resource associated with that service.
        """
        serviceObject = self.core.service_with_region(
            region_name, service_id, base_uri_from_request(request))

        if serviceObject is None:
            # workaround for https://github.com/twisted/klein/issues/56
            return NoResource()
        return serviceObject
