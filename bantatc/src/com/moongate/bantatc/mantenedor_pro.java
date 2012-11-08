package com.moongate.bantatc;
import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.AdapterView;
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
		public String search_code;
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.mantenedor_pro);
				cdHttp = (TextView) this.findViewById(R.id.cdHttp);
				prodCode= (TextView) this.findViewById(R.id.ProductCode);
				
				Bundle extras = getIntent().getExtras();
				
				if(extras ==null) {
					ip = "192.168.1.99";
				}
				else{
					ip = extras.getString("ip");
				}
				this.prodCode = (TextView) this.findViewById(com.moongate.bantatc.R.id.ProductCode);
				this.lv = (ListView) findViewById(R.id.listView1);
				this.lv.setClickable(true);
				
				this.lv.setOnItemClickListener(new AdapterView.OnItemClickListener() {
					public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
						Product p = (Product) parent.getItemAtPosition(position);
						Toast.makeText(
								mantenedor_pro.this, 
								"Clicked!  " +p.code+ " - " + String.valueOf(position)+ ","+ String.valueOf(id),
								Toast.LENGTH_LONG).show();
						mantenedor_pro.this.verProducto(p.code);
					}
				});

				new wsListProducts().execute(this);
    } 
		private void verProducto(String code){
			Intent adm_prod = new Intent(this, Adm_Pro.class);
				adm_prod.putExtra("search_code", code);
				adm_prod.putExtra("ip", this.ip);
				startActivityForResult(adm_prod, 0);
				mantenedor_pro.this.finish();
		}
		public void buscar(View v){
			this.search_code = this.prodCode.getText().toString();
			verProducto(this.search_code);
		}
    public void escanear(View v){
			// intent.putExtra("SCAN_MODE", "QR_CODE_MODE");
			//   intent.putExtra("SCAN_MODE", "PRODUCT_MODE");
			Intent intent = new Intent("com.google.zxing.client.android.SCAN");
			//intent.putExtra("SCAN_FORMATS", "CODE_39,CODE_93,CODE_128,DATA_MATRIX,ITF,CODABAR");
			intent.putExtra("SCAN_MODE", "PRODUCT_MODE");
			startActivityForResult(intent, 0);    //Barcode Scanner to scan for us
		}

    @Override 
		public void onActivityResult(int requestCode, int resultCode, Intent data) {     
			super.onActivityResult(requestCode, resultCode, data); 
			if (data == null){
				//if data == null es para el finish de AdmPro
				mantenedor_pro.this.finish();
			}else{
				if (resultCode == RESULT_OK) {
						String format = data.getStringExtra("SCAN_RESULT_FORMAT");
						String result = data.getStringExtra("SCAN_RESULT");
						Toast.makeText(
								mantenedor_pro.this, 
								"Code " + result + " ["+format+"]",
								Toast.LENGTH_LONG
						).show();
						//TextView pcode = 
						prodCode.setText(result);
						mantenedor_pro.this.buscar(lv);
					} else if (resultCode == RESULT_CANCELED) {

					}
			}
		}	
}