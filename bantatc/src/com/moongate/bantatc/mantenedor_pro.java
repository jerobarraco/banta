package com.moongate.bantatc;


import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;

import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.StatusLine;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.DefaultHttpClient;
import org.json.JSONArray;
import org.json.JSONObject;

import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import java.util.ArrayList;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.json.JSONException;


public class mantenedor_pro extends Activity {
		ArrayList<Product> products;
		private String ip;
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.mantenedor_pro);
				
				Bundle extras = getIntent().getExtras();
				
				if(extras ==null) {
					ip = "192.168.1.99";
				}
				else{
						ip = extras.getString("ip");
				}
				loadProds();
    }
		public void loadProds(){
			String response = this.readProductList();
			JSONObject responseObj = null; 
			try {
				responseObj = new JSONObject(response); 
				JSONArray prodList;
				prodList = responseObj.getJSONArray("prods");
	
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
   //create an ArrayAdaptar from the String Array
		ListView listView = (ListView) findViewById(R.id.listView1);
		listView.setAdapter(
					 new ArrayAdapter(
					 this, android.R.layout.simple_list_item_1, products));
		}
    public String readProductList(){
			//this is completely inneficient, storing the whole string in memory sucks :D
			StringBuilder builder = new StringBuilder();
			HttpClient client = new DefaultHttpClient();
			//harcoded urls sucks too, we need to create a new url.
			//we will probably have to let the user put the ip of the server
			HttpGet httpGet = new HttpGet("http://"+ip+":8080/products/list");
			//HttpGet httpGet = new HttpGet("http://192.168.1.99:8080/products/list");
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
					Log.e(mantenedor_pro.class.toString(), "Failed to download file");
				}
			} catch (ClientProtocolException e) {
				e.printStackTrace();
			} catch (java.io.IOException e) {
				e.printStackTrace();
			}
			return builder.toString();
		}
}