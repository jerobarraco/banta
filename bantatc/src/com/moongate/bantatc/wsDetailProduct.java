package com.moongate.bantatc;
import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.NameValuePair;
import org.apache.http.StatusLine;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.HttpClient;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.HttpDelete;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.message.BasicNameValuePair;
import org.apache.http.params.HttpParams;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

 
import android.app.ProgressDialog;
import android.net.Uri;
import android.os.AsyncTask;
import android.util.Log;
import android.widget.Toast;
import org.apache.http.client.methods.HttpGet;

public class wsDetailProduct extends AsyncTask<Adm_Pro, Void, Product>{
		private Adm_Pro padre;
		private boolean result;
		private String ip, code;

		
		@Override
		protected Product doInBackground(Adm_Pro... class_padre){
			this.padre = class_padre[0];
			this.ip = this.padre.ip;
			this.code = this.padre.search_code;
			this.result = false;
			Product prod = new Product();
			//in case there's an error, we put the code as the code in the product
			//so the editor will show an empy boxes holding the new code
			//this way we can insert a new product only by scanning a code.
			prod.code = this.code ;
			
			List<Product> products = new ArrayList<Product>();
			String response = this.searchProducts();
			JSONObject responseObj; 
			try {
				responseObj = new JSONObject(response);
				JSONArray prodList = responseObj.getJSONArray("data");
				JSONObject prod_info = prodList.getJSONObject(0);
				
				prod.name = prod_info.getString("name");
				prod.code = prod_info.getString("code");
				prod.price = prod_info.getDouble("price");
				prod.stock = prod_info.getDouble("stock");
				this.result = true; // this is enough

			} catch (Exception ex) {
				Logger.getLogger(wsDelProducts.class.getName()).log(Level.SEVERE, null, ex);
			}
			
			return prod;
		}		
		private String searchProducts(){
				//this is completely inneficient, storing the whole string in memory sucks :D
				StringBuilder builder = new StringBuilder();
				HttpClient client = new DefaultHttpClient();
				//harcoded urls sucks too, we need to create a new url.
				//we will probably have to let the user put the ip of the server
				Uri.Builder b = Uri.parse("http://"+this.ip+":8080").buildUpon();
				b.path("/prods");
				b.appendQueryParameter("code", this.code);
				String url = b.build().toString();
				
				HttpGet httpGet = new HttpGet(url);
				try {
					HttpResponse response = client.execute(httpGet);
					StatusLine statusLine = response.getStatusLine();
					int statusCode = statusLine.getStatusCode();
					if (statusCode == 200) {
						HttpEntity entity = response.getEntity();
						InputStream content = entity.getContent();
						BufferedReader reader = new BufferedReader(new InputStreamReader(content));
						String line;
						while ((line = reader.readLine()) != null) {
							builder.append(line);
						}
						return builder.toString();
					} else {
						Log.e(wsListProducts.class.toString(), "Failed to download file");
					}
				} catch (ClientProtocolException e) {
					Log.e(wsListProducts.class.toString(), e.toString());
				} catch (java.io.IOException e) {
					Log.e(wsListProducts.class.toString(), e.toString());
				}
				return builder.toString();
			}
		@Override
		protected void onPostExecute(Product p){
			// esto se ejecuta automaticamente cuadno termina la tarea (doInBackgroudn(
			// recibe como parametro, el resultado de doInBackground (como devuelve Void, recibe nada(
			// Esto se ejecuta en el mismo thread que la GUI, asi que solo aca podemos acceder a la gui
			// aca hay quehacer que muestre un cartel, "ok', o "cac"
			String mensaje ;
			if (this.result){
				mensaje = "Producto encontrado";
			}else{
				mensaje = "No se encontró el producto";
			}
			Toast.makeText( this.padre, mensaje, Toast.LENGTH_LONG).show();
			this.padre.llenar(p);
		}

}

