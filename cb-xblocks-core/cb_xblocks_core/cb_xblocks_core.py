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

"""Some useful XBlock classes."""

__author__ = 'John Orr (jorr@google.com)'


import os
from xml.etree import cElementTree

from controllers import utils
import extensions.tags.gcb
import jinja2
from modules.assessment_tags import questions
from xblock.core import XBlock
from xblock.fields import Integer
from xblock.fields import Scope
from xblock.fields import String
from xblock.fragment import Fragment


class NavItem(object):
    """Class to hold information for the SequenceBlock's navigation bar."""

    def __init__(self, block_id, runtime):
        self.runtime = runtime
        self.icon_class = self.choose_icon_class(block_id) or 'document'

    def choose_icon_class(self, block_id):
        block = self.runtime.get_block(block_id)
        if block.has_children:
            for child_id in block.children:
                icon_class = self.choose_icon_class(child_id)
                if icon_class:
                    return icon_class
            return None
        else:
            if isinstance(block, VideoBlock):
                return 'video'


class SequenceBlock(XBlock):
    """An XBlock which presents its children in a tabbed view."""

    has_children = True

    position = Integer(
        help='Last tab viewed in this sequence',
        scope=Scope.user_state,
        default=0)

    def __init__(self, *args, **kwargs):
        super(SequenceBlock, self).__init__(*args, **kwargs)
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                os.path.join(os.path.dirname(__file__), 'templates')),
            extensions=['jinja2.ext.autoescape'],
            autoescape=True)

    def student_view(self, context=None):
        frag = Fragment()

        frag.add_css_url(
            self.runtime.local_resource_url(self, 'public/css/sequence.css'))
        frag.add_javascript_url(
            self.runtime.local_resource_url(self, 'public/js/sequence.js'))
        frag.initialize_js('SequenceBlock')

        child_frags = self.runtime.render_children(self, context)
        frag.add_frags_resources(child_frags)

        template = self.template_env.get_template('sequence.html')
        template_values = {
            'nav_items': [
                NavItem(child_id, self.runtime) for child_id in self.children],
            'children': child_frags,
            'position': self.position}
        frag.add_content(template.render(template_values))

        return frag

    @XBlock.json_handler
    def on_select(self, data, suffix=''):
        self.position = data.get('position', 0)


class VideoBlock(XBlock, extensions.tags.gcb.YouTube):
    """A XBlock to display YouTube videos."""

    display_name = String(
        display_name='A YouTube Video',
        help='A YouTube Video.',
        default='Video',
        scope=Scope.settings
    )
    youtube_id_1_0 = String(
        display_name='YouTube ID',
        help='The YouTube ID reference for the normal speed video.',
        scope=Scope.settings,
        default='Kdg2drcUjYI'
    )

    def student_view(self, context=None):
        if utils.CAN_PERSIST_TAG_EVENTS.value:
            xml = self._render_with_tracking(self.youtube_id_1_0)
        else:
            xml = self._render_no_tracking(self.youtube_id_1_0)
        return Fragment(unicode(cElementTree.tostring(xml, encoding='utf-8')))


class QuestionBlock(XBlock):
    """An XBlock to embed a Course Builder question inside a XBlock tree."""

    quid = String(
        display_name='Question Id',
        help='The Course Builder ID for the question',
        scope=Scope.settings,
        default=''
    )

    def student_view(self, context=None):
        frag = Fragment()
        frag.add_content(questions.render_question(
            self.quid, self.quid, 'en-US', False, weight=1.0, progress=None))
        return frag