# Copyright 2013 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Bind the App Engine service endpoints."""

__author__ = 'John Orr (jorr@google.com)'

import webapp2

# The following import is needed in order to add third-party libraries
# before loading any other modules.
import appengine_config  # pylint: disable-msg=unused-import

import django.conf
import django.template.loader
import handlers


# The location of the DJango templates used by XBlocks
XBLOCK_TEMPLATES_PATH = 'lib/XBlock/xblock/templates'

if not django.conf.settings.configured:
    django.conf.settings.configure(
        TEMPLATE_DIRS=[XBLOCK_TEMPLATES_PATH])

view_app = webapp2.WSGIApplication([
    ('/js/(.*)', handlers.JsWrapperHandler),
    ('/view', handlers.ViewXblockPageHandler),
], debug=True)

app = webapp2.WSGIApplication([
    ('/handler/(\d*)/(.*)/', handlers.XBlockEndpointHandler),
    ('/login_in_popup', handlers.LoginInPopupPageHandler),
    ('/display_xblock', handlers.DisplayXblockPageHandler),
    ('/rest/xblock', handlers.XblockRestHandler),
    ('/rest/xblock/(\d*)', handlers.XblockRestHandler),
    ('/.*', handlers.DefaultPageHandler),
], debug=True)
