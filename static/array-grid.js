

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
			},
			//extraParams: { test: 'test' }
		},
		autoLoad: true,
        fields: [
           {name: 'code'},
		   {name: 'name'},
           {name: 'price',      type: 'float'},
           {name: 'stock',     type: 'float'},
        ],
		
    });

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
            }            
        ],
        height: 600,
        width: 800,
        title: 'Array Grid',
        renderTo: 'grid-example',
        viewConfig: {
            stripeRows: true
        }
    });
});
