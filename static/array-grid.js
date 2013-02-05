Ext.Loader.setConfig({enabled: true});
Ext.Loader.setPath('Ext.ux', 'ux');
Ext.require([
    'Ext.grid.*',
    'Ext.data.*',
    'Ext.util.*',
    'Ext.toolbar.Paging',
    'Ext.ux.PreviewPlugin',
    'Ext.ModelManager',
    'Ext.tip.QuickTipManager'
]);

Ext.onReady(function() {
    Ext.QuickTips.init();
    
    // create the data store
    var store = new Ext.data.Store({
		proxy: {
			type: 'ajax',
			url: '/prods/',
			reader: {
				type: 'json',
				root: 'data'
			},
			writer: {
				type: 'json',
				root: 'data'
			},
			actionMethods: {
				create: 'POST', read: 'GET', update: 'POST', destroy: 'POST'
			}
			//extraParams: { test: 'test' }
		},
		autoLoad: true,
        fields: [
           {name: 'code'},
		   {name: 'name'},
           {name: 'price',     type: 'float'},
           {name: 'stock',     type: 'float'},
           {name: 'thumb',     type: 'str'},

        ]
		
    });
    function renderProduct(value, p, record) {
        return Ext.String.format(
            '<img src="{0}"/>',
            value,
            record.data.code,
			record.data.price,
            record.getId(),
            record.data.thumb
        );
    }
    // create the Grid
    var grid = new Ext.grid.Panel({
        store: store,
        //stateful: true,
        //stateId: 'stateGrid',
        columns: [
            {
                text     : 'Code',
                sortable : true,
                dataIndex: 'code'
            },
			{
                text     : 'Name',
                width    : 75,
                sortable : true,
                dataIndex: 'name'
            },
            {
                text     : 'Price',
                width    : 75,
                sortable : true,
                renderer : 'usMoney',
                dataIndex: 'price'
            },
            {
                text     : 'Stock',
                width    : 75,
                sortable : true,
                dataIndex: 'stock'
            }         ,
            {
                text     : 'thumb',
                width    : 75,
                sortable : true,
                dataIndex: 'thumb',
                renderer:renderProduct
            }

        ],
        height: 620,
        width: 800,
        title: 'Banta',
        renderTo: 'grid-example',
        viewConfig: {
            //stripeRows: true,
            id: 'gv',
            trackOver: false,
            stripeRows: false,
            plugins: [{
                ptype: 'preview',
                bodyField: 'name',
                expanded: true,
                pluginId: 'preview'
            }]
        },
        bbar: Ext.create('Ext.PagingToolbar', {
            store: store,
            displayInfo: true,
            displayMsg: 'Displaying topics {0} - {1} of {2}',
            emptyMsg: "No topics to display",
            items:[
                '-', {
                    text: 'Show Preview',
                    pressed: false,
                    enableToggle: true,
                    toggleHandler: function(btn, pressed) {
                        var preview = Ext.getCmp('gv').getPlugin('preview');
                        preview.toggleExpanded(pressed);
                    }
                }]
        })
    });
});
