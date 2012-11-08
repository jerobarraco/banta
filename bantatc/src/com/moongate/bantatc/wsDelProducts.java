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
import android.os.AsyncTask;
import android.util.Log;
import android.widget.Toast;

public class wsDelProducts extends AsyncTask<Adm_Pro, Void, Void>{
		private Adm_Pro padre;
		private boolean result;
		private String ip, code;

		
		@Override
		protected Void doInBackground(Adm_Pro... class_padre){
			this.padre = class_padre[0];
			ip = this.padre.ip;
			code = this.padre.code;


			
			StringBuilder sb = new StringBuilder();
			HttpClient client = new DefaultHttpClient();
			HttpDelete post = new HttpDelete("http://"+ip+":8080/prods?code="+code+"");	
			this.result = false;		
			
			try{
				
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
						Log.e(wsDelProducts.class.toString(), e.toString());
			} catch (java.io.IOException e) {
					Log.e(wsDelProducts.class.toString(), e.toString());
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
				mensaje = "Se ha eliminado el producto";
			}else{
				mensaje = "Error al eliminar el producto";
			}
			Toast.makeText( this.padre, mensaje, Toast.LENGTH_LONG).show();
			this.padre.terminar();
			return;
		}

}

