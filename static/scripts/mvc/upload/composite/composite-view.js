define(["utils/utils","mvc/upload/upload-model","mvc/upload/composite/composite-row","mvc/ui/ui-popover","mvc/ui/ui-select","mvc/ui/ui-misc"],function(a,b,c,d,e,f){return Backbone.View.extend({select_extension:null,select_genome:null,collection:new b.Collection,initialize:function(a){this.app=a,this.options=a.options,this.list_extensions=a.list_extensions,this.list_genomes=a.list_genomes;var b=this;this.setElement(this._template()),this.btnStart=new f.Button({title:"Start",onclick:function(){b._eventStart()}}),this.btnClose=new f.Button({title:"Close",onclick:function(){b.app.modal.hide()}});var c=[this.btnStart,this.btnClose];for(var d in c)this.$("#upload-buttons").prepend(c[d].$el);this.select_extension=new e.View({css:"footer-selection",container:this.$("#footer-extension"),data:_.filter(this.list_extensions,function(a){return a.composite_files}),onchange:function(a){b.collection.reset();var c=_.findWhere(b.list_extensions,{id:a});if(c&&c.composite_files)for(var d in c.composite_files){var e=c.composite_files[d];b.collection.add({id:b.collection.size(),file_name:"<b>-</b>",file_desc:e.description||e.name||"Unavailable"})}}}),this.$("#footer-extension-info").on("click",function(a){b._showExtensionInfo({$el:$(a.target),title:b.select_extension.text(),extension:b.select_extension.value(),placement:"top"})}).on("mousedown",function(a){a.preventDefault()}),this.select_genome=new e.View({css:"footer-selection",container:this.$("#footer-genome"),data:this.list_genomes,value:this.options.default_genome}),this.collection.on("add",function(a){b._eventAnnounce(a)}),this.collection.on("change add",function(){b._updateScreen()}),this.select_extension.options.onchange(this.select_extension.value())},_eventAnnounce:function(a){var b=new c(this,{model:a});this.$("#upload-table > tbody:first").append(b.$el),b.render(),this.collection.length>0?this.$("#upload-table").show():this.$("#upload-table").hide()},_eventStart:function(){var a=this;this.collection.each(function(b){b.set("genome",a.select_genome.value()),b.set("extension",a.select_extension.value())}),$.uploadpost({url:this.app.options.nginx_upload_path,data:this.app.toData(this.collection.filter()),success:function(b){a._eventSuccess(b)},error:function(b){a._eventError(b)},progress:function(b){a._eventProgress(b)}})},_eventProgress:function(a){this.collection.each(function(b){b.set("percentage",a)})},_eventSuccess:function(){this.collection.each(function(a){a.set("status","success")}),Galaxy.currHistoryPanel.refreshContents()},_eventError:function(a){this.collection.each(function(b){b.set("status","error"),b.set("info",a)})},_showExtensionInfo:function(a){var b=a.$el,c=a.extension,e=a.title,f=_.findWhere(this.list_extensions,{id:c});this.extension_popup&&this.extension_popup.remove(),this.extension_popup=new d.View({placement:a.placement||"bottom",container:b,destroy:!0}),this.extension_popup.title(e),this.extension_popup.empty(),this.extension_popup.append(this._templateDescription(f)),this.extension_popup.show()},_updateScreen:function(){var a=this.collection.first();a&&"running"==a.get("status")?(this.select_genome.disable(),this.select_extension.disable(),this.$("#upload-info").html("Please wait...")):(this.select_genome.enable(),this.select_extension.enable(),this.$("#upload-info").html("You can Drag & Drop files into the rows.")),this.collection.where({status:"ready"}).length==this.collection.length?this.btnStart.enable():this.btnStart.disable(),this.collection.length>0?this.$("#upload-table").show():this.$("#upload-table").hide()},_templateDescription:function(a){if(a.description){var b=a.description;return a.description_url&&(b+='&nbsp;(<a href="'+a.description_url+'" target="_blank">read more</a>)'),b}return"There is no description available for this file extension."},_template:function(){return'<div class="upload-view-composite"><div class="upload-top"><h6 id="upload-info" class="upload-info"/></div><div id="upload-footer" class="upload-footer"><span class="footer-title">Composite Type:</span><span id="footer-extension"/><span id="footer-extension-info" class="upload-icon-button fa fa-search"/> <span class="footer-title">Genome/Build:</span><span id="footer-genome"/></div><div id="upload-box" class="upload-box"><table id="upload-table" class="ui-table-striped" style="display: none;"><thead><tr><th/><th/><th>Description</th><th>Name</th><th>Size</th><th>Settings</th><th>Status</th></tr></thead><tbody></tbody></table></div><div id="upload-buttons" class="upload-buttons"/></div>'}})});
//# sourceMappingURL=../../../../maps/mvc/upload/composite/composite-view.js.map