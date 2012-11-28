package com.moongate.bantatc;

import com.moongate.bantatc.R;
import android.app.ProgressDialog;
import android.net.Uri;
import android.os.AsyncTask;
import android.util.Log;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.TextView;
import java.io.BufferedReader;
import java.io.InputStream;

import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.StatusLine;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.params.HttpParams;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

public class wsListProducts extends AsyncTask<mantenedor_pro, Void, ArrayList<Product>> {
	private boolean error = false;

	private ProgressDialog dialog;
	public ArrayList<Product> products;	 
	private mantenedor_pro padre;
		  
	@Override
	protected void onPreExecute() {
	// dialog.setMessage("Getting your data... Please wait...");
	 //dialog.show();
	}

	@Override
	protected ArrayList<Product> doInBackground(mantenedor_pro... class_padre) {
		this.padre = class_padre[0];
		// TODO Auto-generated method stub
		//this.dialog = new ProgressDialog(padre);
		String response = this.readProductList(class_padre[0].ip);
		JSONObject responseObj = null; 
		products = new ArrayList<Product>();
			
		try {
			responseObj = new JSONObject(response); 
			JSONArray prodList;
			prodList = responseObj.getJSONArray("data");

			products = new ArrayList<Product>();
			for (int i=0; i<prodList.length(); i++){
				//get the country information JSON object
				 JSONObject prod_info = prodList.getJSONObject(i);
				//create java object from the JSON object
				Product prod = new Product();
				prod.name = prod_info.getString("name");
				prod.code = prod_info.getString("code");
				prod.price = prod_info.getDouble("price");
				prod.stock = prod_info.getDouble("stock");

				//add to country array list
				products.add(prod);
			}
		} catch (JSONException ex) {
					Logger.getLogger(mantenedor_pro.class.getName()).log(Level.SEVERE, null, ex);
			}
			return products;
		}
		public String readProductList(String ip){
			//this is completely inneficient, storing the whole string in memory sucks :D
			StringBuilder builder = new StringBuilder();
			HttpClient client = new DefaultHttpClient();
			//harcoded urls sucks too, we need to create a new url.
			//we will probably have to let the user put the ip of the server
			Uri.Builder b = Uri.parse("http://"+ip+":8080").buildUpon();
			b.path("/prods");
			
			b.appendQueryParameter("start", "0");
			b.appendQueryParameter("limit", "100");//todo, poner estas  (por ejemplo, this.padre.limit y this.padre.start
			b.appendQueryParameter("search_name", this.padre.search_name);
			b.appendQueryParameter("order_by", this.padre.order_by);
			b.appendQueryParameter("order_asc", this.padre.order_asc);
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
	public void onPostExecute(ArrayList<Product> products){
		if (this.padre != null){
		Adapter_Pro nuevo_adapter = new Adapter_Pro(this.padre,R.layout.productview, products);
			this.padre.lv.setAdapter(nuevo_adapter);
			//nuevo_adapter.notifyDataSetChanged();
			this.padre.cdHttp.setText("Cargados " +String.valueOf(products.size())+" productos"); 
		}
	}
}
		
