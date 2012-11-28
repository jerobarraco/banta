package com.moongate.bantatc;
import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;
import android.widget.AdapterView;
import android.widget.Button;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;
import com.moongate.bantatc.R;
import java.util.ArrayList;

public class mantenedor_pro extends Activity {
		ArrayList<Product> products;
		public String ip;
		TextView cdHttp ;
		ListView lv;
		TextView prodCode;
		public String [] ordenes = {"stock", "name", "price", "code" };
		public String search_code = "";
		public String search_name = "";
		public String order_by = ordenes[0];
		public String order_asc = "1";
		
		@Override
		public boolean onCreateOptionsMenu(Menu menu) {
				MenuInflater inflater = getMenuInflater();
				inflater.inflate(R.menu.activity_mantenedor__producto, menu);
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
				this.recargar();
				return true;
		}
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.mantenedor_pro);
				cdHttp = (TextView) this.findViewById(R.id.cdHttp);
				prodCode= (TextView) this.findViewById(R.id.ProductCode);
				
				Bundle extras = getIntent().getExtras();
				
				this.prodCode = (TextView) this.findViewById(com.moongate.bantatc.R.id.ProductCode);
				this.lv = (ListView) findViewById(R.id.listView1);
				
				if(extras ==null) {
					ip = getResources().getString(R.string.default_ip);
				}
				else{
					ip = extras.getString("ip");				
				}
				this.lv.setClickable(true);	
				this.lv.setOnItemClickListener(new AdapterView.OnItemClickListener() {
					public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
						Product p = (Product) parent.getItemAtPosition(position);
						/*Toast.makeText(
								mantenedor_pro.this, 
								"Clicked!  " +p.code+ " - " + String.valueOf(position)+ ","+ String.valueOf(id),
								Toast.LENGTH_LONG).show();*/
						mantenedor_pro.this.verProducto(p.code);
					}
				});
				this.search_name = "";
				this.search_code = "";
				
				recargar();
    } 
		private void verProducto(String code){
			Intent adm_prod = new Intent(this, Adm_Pro.class);
			adm_prod.putExtra("search_code", code);
			adm_prod.putExtra("ip", this.ip);
			startActivityForResult(adm_prod, 0);
		}
	public void buscar(View v){
		this.search_name = this.prodCode.getText().toString();
		//verProducto(this.search_code);
		recargar();
	}
		
	public void escanear(View v){
		// intent.putExtra("SCAN_MODE", "QR_CODE_MODE");
		//   intent.putExtra("SCAN_MODE", "PRODUCT_MODE");
		Intent intent = new Intent("com.google.zxing.client.android.SCAN");
		//intent.putExtra("SCAN_FORMATS", "CODE_39,CODE_93,CODE_128,DATA_MATRIX,ITF,CODABAR");
		intent.putExtra("SCAN_MODE", "PRODUCT_MODE");
		startActivityForResult(intent, 0);    //Barcode Scanner to scan for us
	}
	public void recargar(){
		cdHttp.setText("Cargando...");
		new wsListProducts().execute(this);
	}
	@Override 
	public void onActivityResult(int requestCode, int resultCode, Intent data) {     
		super.onActivityResult(requestCode, resultCode, data); 
		if (data == null){
			//if data == null es para el finish de AdmPro
			//cuando vuelve de adm_pro, recargamos la lista
			recargar();
		}else{
			if (resultCode == RESULT_OK) {
				String format = data.getStringExtra("SCAN_RESULT_FORMAT");
				String result = data.getStringExtra("SCAN_RESULT");
				Toast.makeText(
						mantenedor_pro.this, 
						"Codigo: " + result + " ["+format+"]",
						Toast.LENGTH_LONG
				).show();
				//TextView pcode = 
				//prodCode.setText(result);
				mantenedor_pro.this.verProducto(result);
			} else if (resultCode == RESULT_CANCELED) {

			}
		}
	}	
}