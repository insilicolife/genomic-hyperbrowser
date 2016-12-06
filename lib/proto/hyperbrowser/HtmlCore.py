from proto.HtmlCore import HtmlCore as ProtoHtmlCore


class HtmlCore(ProtoHtmlCore):
    def tableHeader(self, headerRow, tagRow=None, tableId=None,
                    addInstruction=False, **kwargs):
        if addInstruction:
            if not tableId:
                tableId = 'tab0'
            self.addInstruction(tableId=tableId)
        super(HtmlCore, self).tableHeader(headerRow, tagRow=tagRow,
                                          tableId=tableId, **kwargs)

    def addInstruction(self, tableId='tab0'):
        tableId = str(tableId).replace('"', '')

        self._str += """
<br \>
<div  style="margin-bottom:10px;" class="infomessage">
<div class='%sclickmeTable'>Show instructions for table</div></div>
""" % tableId

        self._str += """
<div id ='%stable'  style='display:none;min-width:400px;margin-top:10px;margin-bottom:10px;border:1px solid #000033;padding:10px;color:#181818' >
<div id ='guideLine'  style='font-weight:bold;text-transform:uppercase;margin-bottom:5px;'>
Guidelines for table:
</div>

<div id ='option1d'  style='font-weight:bold;margin-bottom:5px;margin-top:5px;'>
Sorting:
</div>
- To sort the table by a column, click on the column header. <br \>

<div id ='option1d'  style='font-weight:bold;margin-bottom:5px;margin-top:5px;'>
Show/Hide plots:
</div>
- To generate a bar plot for a specific column check the box (when there is one) next to the column header. The sorting in the table is also reflected in the plots.
</div>
""" % tableId

        self._str += """
<script>
$('.%sclickmeTable').on('click', function(e) {
    //console.log('#%sTable');
    $('#%stable').slideToggle('fast');
});
</script>
""" % ((tableId,) * 3)
        
        return self
