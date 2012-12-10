package com.moongate.bantatc;
import org.json.JSONArray;
import org.json.JSONObject;

 
import android.net.Uri;
import android.os.AsyncTask;
import android.util.Log;
import android.widget.Toast;
import org.apache.http.client.methods.HttpGet;

public class wsDetailProduct extends AsyncTask<Adm_Pro, Void, Product>{
		private Adm_Pro padre;
		private String code;
		private wsBase ws = new wsBase();
		
		@Override
		protected Product doInBackground(Adm_Pro... class_padre){
			this.padre = class_padre[0];
			this.code = this.padre.search_code;

			//harcoded urls sucks too, we need to create a new url.
			//we will probably have to let the user put the ip of the server
			Uri.Builder b = Uri.parse("http://"+Pref.ip+":8080").buildUpon();
			b.path("/prods");
			b.appendQueryParameter("search_code", this.code );
			String url = b.build().toString();	
			HttpGet httpGet = new HttpGet(url);

			JSONObject responseObj = this.ws.doRequest(httpGet); 
			return this.decodeJSON(responseObj);
		}
		private Product decodeJSON(JSONObject r){
			Product prod = new Product();
			//in case there's an error, we put the code as the code in the product
			//so the editor will show an empy boxes holding the new code
			//this way we can insert a new product only by scanning a code.
			prod.code = this.code ;
			if (this.ws.success){
				try {
					JSONArray prodList = r.getJSONArray("data");
					JSONObject prod_info = prodList.getJSONObject(0);

					prod.name = prod_info.getString("name");
					prod.code = prod_info.getString("code");
					prod.price = prod_info.getDouble("price");
					prod.stock = prod_info.getDouble("stock");
				} catch (Exception ex) {
					this.ws.success = false;
					this.ws.error = ex.toString();
					Log.e(wsDetailProduct.class.getName(), this.ws.error);
				}
			}
			//finalmente devolvemos prod
			return prod;
		}		

		@Override
		protected void onPostExecute(Product p){
			// esto se ejecuta automaticamente cuadno termina la tarea (doInBackgroudn(
			// recibe como parametro, el resultado de doInBackground (como devuelve Void, recibe nada(
			// Esto se ejecuta en el mismo thread que la GUI, asi que solo aca podemos acceder a la gui
			// aca hay quehacer que muestre un cartel, "ok', o "cac"
			String mensaje ;
			if (this.ws.success){
				mensaje = "Producto encontrado";
			}else{
				mensaje = "Error. "+this.ws.error;
			}
			Toast.makeText( this.padre, mensaje, Toast.LENGTH_LONG).show();
			this.padre.llenar(p);
		}

}

