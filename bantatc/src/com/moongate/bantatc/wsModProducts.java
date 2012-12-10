package com.moongate.bantatc;

import android.os.AsyncTask;
import android.util.Log;
import android.widget.Toast;
import java.io.UnsupportedEncodingException;
import java.util.ArrayList;
import java.util.List;
import org.apache.http.NameValuePair;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.message.BasicNameValuePair;
import org.apache.http.protocol.HTTP;
import org.json.JSONObject;

public class wsModProducts extends AsyncTask<Adm_Pro, Void, Void>{
	private Adm_Pro padre;
	private String code, old_code, name;
	private Double price, stock;
	private wsBase ws = new wsBase();
	
	@Override
	protected Void doInBackground(Adm_Pro... class_padre){
			this.padre = class_padre[0];
			old_code = this.padre.old_code;
			code = this.padre.code;
			name = this.padre.name;
			price = this.padre.price;
			stock = this.padre.stock;

			//Este es el request mas complicado, porque hay que pasar los parametros en el cuerpo
			//y no en la url
			HttpPost post = new HttpPost("http://"+Pref.ip+":8080/prods");
			//creamos los parámetros
			List<NameValuePair> nameValuePairs = new ArrayList<NameValuePair>(5);
			//agregamos los parametros
			nameValuePairs.add(new BasicNameValuePair("old_code", this.old_code));
			nameValuePairs.add(new BasicNameValuePair("code", this.code));
			nameValuePairs.add(new BasicNameValuePair("name", this.name));
			nameValuePairs.add(new BasicNameValuePair("price", this.price.toString() ) );
			nameValuePairs.add(new BasicNameValuePair("stock", this.stock.toString() ) );
			try {
				//y los metemos en el post. EL UTF ES IMPORTANTE!
				post.setEntity(new UrlEncodedFormEntity(nameValuePairs, HTTP.UTF_8));
				JSONObject obj = this.ws.doRequest(post);
			} catch (UnsupportedEncodingException ex) {
				this.ws.success = false;
				this.ws.error = ex.toString();
				Log.e(wsModProducts.class.getName(), this.ws.error);
			}
			//no necesitamos decodificar el objeto, si el wsBase no dio error es porque todo salio bien
			return null;
	}
	@Override
	protected void onPostExecute(Void asd){
		// esto se ejecuta automaticamente cuadno termina la tarea (doInBackgroudn(
		// recibe como parametro, el resultado de doInBackground (como devuelve Void, recibe nada(
		// Esto se ejecuta en el mismo thread que la GUI, asi que solo aca podemos acceder a la gui
		// aca hay quehacer que muestre un cartel, "ok', o "cac"
		String mensaje ;
		if (this.ws.success){
			mensaje = "Guardado correctamente";
		}else{
			mensaje = "Error. " + this.ws.error;
		}
		
		Toast.makeText(this.padre, mensaje, Toast.LENGTH_LONG).show();
		this.padre.terminar();
		return;
	}
	
}
