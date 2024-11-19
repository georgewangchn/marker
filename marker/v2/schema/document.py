from __future__ import annotations

from typing import List

from pydantic import BaseModel

from marker.v2.schema import BlockTypes
from marker.v2.schema.blocks import Block, BlockId, BlockOutput
from marker.v2.schema.groups.page import PageGroup


class DocumentOutput(BaseModel):
    children: List[BlockOutput]
    html: str
    block_type: BlockTypes = BlockTypes.Document


class Document(BaseModel):
    filepath: str
    pages: List[PageGroup]
    block_type: BlockTypes = BlockTypes.Document

    def get_block(self, block_id: BlockId):
        page = self.get_page(block_id.page_id)
        block = page.get_block(block_id)
        if block:
            return block
        return None

    def get_page(self, page_id):
        for page in self.pages:
            if page.page_id == page_id:
                return page
        return None

    def get_next_block(self, block: Block):
        page = self.get_page(block.page_id)
        next_block = page.get_next_block(block)
        if next_block:
            return next_block
        next_page = self.get_next_page(page)
        if not next_page:
            return None
        return next_page.get_block(next_page.structure[0])

    def get_next_page(self, page: PageGroup):
        page_idx = self.pages.index(page)
        if page_idx + 1 < len(self.pages):
            return self.pages[page_idx + 1]
        return None

    def assemble_html(self, child_blocks: List[Block]):
        template = ""
        for c in child_blocks:
            template += f"<content-ref src='{c.id}'></content-ref>"
        return template

    def render(self):
        child_content = []
        for page in self.pages:
            child_content.append(page.render(self, None))

        return DocumentOutput(
            children=child_content,
            html=self.assemble_html(child_content)
        )
