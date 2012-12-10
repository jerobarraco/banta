package com.moongate.bantatc;
import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;
import android.widget.AbsListView;
import android.widget.AbsListView.OnScrollListener;
import android.widget.AdapterView;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;
import com.moongate.bantatc.R;

public class mantenedor_pro extends Activity implements OnScrollListener{
		TextView cdHttp ;
		ListView lv;
		TextView prodCode;
		public String [] ordenes = {"stock", "name", "price", "code" };
		public String search_code = "";
		public String search_name = "";
		public String order_by = ordenes[0];
		public String order_asc = "1";
		public Adapter_Pro adapter;
		//para cargar al scrollear
		//indica la cantidad de elementos a intenar cargar por pagina
		public int cargar = 20;
		//indica la pagina actual
		public int pagina = 0;
		//evita cargar 2 veces (aunque seria mejor utilizar una instancia de wsListProducts para evitar tener que usar un flag)
		public boolean cargando = false;
		//indica la cantidad minima visible antes de intentar cargar nueamente
		private int visibles = 5;
		
		public int total = 0;
		//indica si llegamos al fin de la lista... 
		public boolean end;
		
		
		@Override
		public boolean onCreateOptionsMenu(Menu menu) {
				MenuInflater inflater = getMenuInflater();
				inflater.inflate(R.menu.activity_mantenedor__producto, menu);
				//aca podriamos verificar si la versin del sdk es <14 entonces ocultamos el boton de menu que hicimos aparte
				//o tamb podriamos poner a los items que se muestren en el action bar
				
				return true;
				
		}
		@Override
		public boolean onOptionsItemSelected(MenuItem item) {
				// Handle item selection
				switch (item.getItemId()) {
						case R.id.mpmenu_refresh :
							break;
						case R.id.mpmenu_change:
							if (this.order_asc.equals("1")){
								this.order_asc = "0";
							} else{
								this.order_asc = "1";
							}
							break;
						case R.id.mpmenu_by_stock:
							this.order_by = ordenes[0];
							break;
						case R.id.mpmenu_by_name:
							this.order_by = ordenes[1];
							break;
						case R.id.mpmenu_by_price :
							this.order_by = ordenes[2];
							break;
						
						case R.id.mpmenu_by_code:
							this.order_by = ordenes[3];
							break;
						default:
							return super.onOptionsItemSelected(item);
				}
				this.recargar(true);
				return true;
		}
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.mantenedor_pro);
				this.search_name = "";
				this.search_code = "";
				this.cargando = false;
				this.cdHttp = (TextView) this.findViewById(R.id.cdHttp);
				this.prodCode = (TextView) this.findViewById(R.id.ProductCode);
				this.lv = (ListView) findViewById(R.id.listView1);
				
				this.lv.setClickable(true);	
				this.lv.setOnItemClickListener(new AdapterView.OnItemClickListener() {
					public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
						Product p = (Product) parent.getItemAtPosition(position);
						mantenedor_pro.this.verProducto(p.code);
					}
				});
				this.adapter = new Adapter_Pro(this, R.layout.productview);
				this.lv.setAdapter(this.adapter);
				//el orden de estas dos lineas es very muy important, sino la lista intentará cargar mas.. y eso hara macana
				recargar(true);
				this.lv.setOnScrollListener(this);
    } 
	private void verProducto(String code){
		Intent adm_prod = new Intent(this, Adm_Pro.class);
		adm_prod.putExtra("search_code", code);
		startActivityForResult(adm_prod, 0);
	}
	public void buscar(View v){
		this.search_name = this.prodCode.getText().toString();
		recargar(true);
	}
		
	public void escanear(View v){
		// intent.putExtra("SCAN_MODE", "QR_CODE_MODE");
		//   intent.putExtra("SCAN_MODE", "PRODUCT_MODE");
		Intent intent = new Intent("com.google.zxing.client.android.SCAN");
		//intent.putExtra("SCAN_FORMATS", "CODE_39,CODE_93,CODE_128,DATA_MATRIX,ITF,CODABAR");
		intent.putExtra("SCAN_MODE", "PRODUCT_MODE");
		startActivityForResult(intent, 0);    //Barcode Scanner to scan for us
	}
	
	public void recargar(boolean reset){
		if (cargando){
			//ojo con esto, si la flag cargando no se coloca a false, podemos quedar trabados eternametne
			return;
		}
		if (reset){
			cdHttp.setText("Cargando...");
			this.pagina = 0;
			this.end = false;
		}else{
				cdHttp.setText("Cargando más...");
				this.pagina ++;
		}
		this.cargando = true;
		new wsListProducts().execute(this);
	}
	
	@Override 
	public void onActivityResult(int requestCode, int resultCode, Intent data) {     
		super.onActivityResult(requestCode, resultCode, data); 
		if (data == null){
			//if data == null es para el finish de AdmPro
			//cuando vuelve de adm_pro, recargamos la lista
			//notar que ponemos true en reset porque si algun dato se modifico, pos, ya toda la lista cambia
			//porque o se puede agregar o quitar un art (hay filtros)
			//o la ubicacion puede cambiar (hay orden)
			recargar(true);
		}else{
			if (resultCode == RESULT_OK) {
				String format = data.getStringExtra("SCAN_RESULT_FORMAT");
				String result = data.getStringExtra("SCAN_RESULT");
				Toast.makeText(
						mantenedor_pro.this, 
						"Codigo: " + result + " ["+format+"]",
						Toast.LENGTH_LONG
				).show();
				mantenedor_pro.this.verProducto(result);
			} else if (resultCode == RESULT_CANCELED) {

			}
		}
	}	

	public void onScrollStateChanged(AbsListView alv, int i) {
		//no necesitamos esta wea
	}

	public void onScroll(AbsListView view, int firstVisibleItem,
                int visibleItemCount, int totalItemCount) {
		//cuando la lista se scrollea
		if ((!end) && (!cargando)  && (totalItemCount - visibleItemCount) <= (firstVisibleItem + visibles)) {
			//si resulta que no estamos cargando... y resulta que la lista scrolleo tanto que estamos en los ultimso x items
				recargar(false);
		}
	}
	public void menu(View v){
		mantenedor_pro.this.openOptionsMenu();
	}
}