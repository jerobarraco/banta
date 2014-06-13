package com.moongate.bantatc;
import android.os.AsyncTask;
import android.widget.Toast;
import org.apache.http.client.methods.HttpDelete;
import org.json.JSONObject;

public class wsDelProduct extends AsyncTask<Adm_Pro, Void, Void>{
		private Adm_Pro padre;
		private String code;
		private wsBase ws = new wsBase();
		
		@Override
		protected Void doInBackground(Adm_Pro... class_padre){
			this.padre = class_padre[0];
			code = this.padre.code;
			//Crear el query para el delete
			HttpDelete del = new HttpDelete("http://"+Pref.ip+":"+Pref.port+"/prods?code="+code+"");	
			//lanzar el query
			JSONObject res = ws.doRequest(del);
			//la verdad que el resultado no importa, el error lo maneja el ws		
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
				mensaje = "Producto eliminado";
			}else{
				mensaje = "Error. " + this.ws.error;
			}
			Toast.makeText( this.padre, mensaje, Toast.LENGTH_LONG).show();
			//hacemos que cierre el editor (AdmPro)
			this.padre.terminar();
			return;
		}

}
