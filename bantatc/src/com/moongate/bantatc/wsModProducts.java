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
import org.apache.http.params.HttpParams;
import android.os.AsyncTask;
import android.util.Log;
import android.widget.Toast;
import java.io.UnsupportedEncodingException;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.apache.http.NameValuePair;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.message.BasicNameValuePair;
// probablemente haya que importar cosas de ahi abajo


public class wsModProducts extends AsyncTask<Adm_Pro, Void, Void>{
	private Adm_Pro padre;
	private boolean result;
	private String ip, code, old_code, name;
	private Double price, stock;
	
	@Override
	protected Void doInBackground(Adm_Pro... class_padre){
			this.padre = class_padre[0];
			ip = this.padre.ip;
			old_code = this.padre.old_code;
			code = this.padre.code;
			name = this.padre.name;

			price = this.padre.price;
			stock = this.padre.stock;

			
			StringBuilder sb = new StringBuilder();
			HttpClient client = new DefaultHttpClient();
			HttpPost post = new HttpPost("http://"+ip+":8080/prods");
			HttpParams params = post.getParams();
			
			this.result = false;
			//TODO agregar parametros
			List<NameValuePair> nameValuePairs = new ArrayList<NameValuePair>(5);
			nameValuePairs.add(new BasicNameValuePair("old_code", this.old_code));
			nameValuePairs.add(new BasicNameValuePair("code", this.code));
			nameValuePairs.add(new BasicNameValuePair("name", this.name));
			nameValuePairs.add(new BasicNameValuePair("price", this.price.toString() ) );
			nameValuePairs.add(new BasicNameValuePair("stock", this.stock.toString() ) );

			try{
				post.setEntity(new UrlEncodedFormEntity(nameValuePairs));
				
				HttpResponse response = client.execute(post);
				StatusLine stat = response.getStatusLine();
				int statcode = stat.getStatusCode();
				if (statcode ==200){
					this.result = true; // this is enough
					HttpEntity entity = response.getEntity();
					InputStream content = entity.getContent();
					//esto puede mejorarse, cuando me acuerde como lo corrijo
					BufferedReader reader = new BufferedReader(new InputStreamReader(content));
					String line;
					
					while ((line=reader.readLine()) != null){
						sb.append(line);
					}
					
				} 
			}	catch (ClientProtocolException e) {
						Log.e(wsModProducts.class.toString(), e.toString());
			} catch (java.io.IOException e) {
					Log.e(wsModProducts.class.toString(), e.toString());
			}
			return null;
	}
		
	@Override
	protected void onPostExecute(Void asd){
		// esto se ejecuta automaticamente cuadno termina la tarea (doInBackgroudn(
		// recibe como parametro, el resultado de doInBackground (como devuelve Void, recibe nada(
		// Esto se ejecuta en el mismo thread que la GUI, asi que solo aca podemos acceder a la gui
		// aca hay quehacer que muestre un cartel, "ok', o "cac"
		String mensaje ;
		if (this.result){
			mensaje = "Guardado correctamente";
		}else{
			mensaje = "Error al guardar";
		}
		
		Toast.makeText( this.padre, mensaje, Toast.LENGTH_LONG).show();
		this.padre.terminar();
		return;
	}
	
}
