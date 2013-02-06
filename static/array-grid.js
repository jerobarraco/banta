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
    var form = '<form action="https://www.paypal.com/cgi-bin/webscr" method="post">\
        <input type="hidden" name="cmd" value="_xclick">\
        <input type="hidden" name="business" value="jerobarraco@yahoo.com.ar">\
        <input type="hidden" name="lc" value="AR">\
        <input type="hidden" name="item_name" value="{1}">\
        <input type="hidden" name="item_number" value="{2}">\
        <input type="hidden" name="amount" value="{3}">\
        <input type="hidden" name="currency_code" value="USD">\
        <input type="hidden" name="button_subtype" value="services">\
        <input type="hidden" name="no_note" value="0">\
        <input type="hidden" name="cn" value="Dar instrucciones especiales al vendedor:">\
        <input type="hidden" name="no_shipping" value="2">\
        <input type="hidden" name="undefined_quantity" value="1">\
        <input type="hidden" name="bn" value="PP-BuyNowBF:btn_buynow_SM.gif:NonHosted">\
        <input type="image" src="https://www.paypalobjects.com/en_US/i/btn/btn_buynow_SM.gif" border="0" name="submit" alt="PayPal - The safer, easier way to pay online! Powered by Banta">\
        <img alt="" border="0" src="https://www.paypalobjects.com/es_XC/i/scr/pixel.gif" width="1" height="1">\
        </form>';


    function renderProduct(value, p, record) {
        return Ext.String.format(
            '<img src="{0}"/>' + form,
            value,
            record.data.name,
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
            /*plugins: [{
                ptype: 'preview',
                bodyField: 'name',
                expanded: true,
                pluginId: 'preview'
            }]*/
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
