package com.moongate.bantatc;

import org.apache.http.client.methods.HttpGet;

import android.net.Uri;
import android.os.AsyncTask;
import android.widget.Toast;


public class wsTestCon extends AsyncTask<Configuracion, Void, Void> {
	private wsBase ws = new wsBase();
	private Configuracion padre;
	
	@Override
	protected Void doInBackground(Configuracion... params) {
		// TODO Auto-generated method stub
		padre = params[0];
		Uri.Builder b = Uri.parse("http://"+padre.c_esrv+":"+padre.c_eport).buildUpon();
		b.path("/prods"); // /prod= productos; /reports = reportes; / 
		b.appendQueryParameter("limit", "0");
		String url = b.build().toString();

		HttpGet httpGet = new HttpGet(url);
		this.ws.doRequest(httpGet);
		
				return null;
	}
	@Override
	protected void onPostExecute(Void conn){
			// esto se ejecuta automaticamente cuadno termina la tarea (doInBackgroudn(
			// recibe como parametro, el resultado de doInBackground (como devuelve Product , recibe un product)
			// Esto se ejecuta en el mismo thread que la GUI, asi que solo aca podemos acceder a la gui
			// aca hay que hacer que muestre un cartel, "ok', o "cac"
			String mensaje ;
			if (this.ws.success){
				mensaje = "Conexion Establecida";
			}else{
				mensaje = "Error "+this.ws.error;
			}
			
			Toast.makeText( this.padre, mensaje, Toast.LENGTH_LONG).show();
	}
	}
	

