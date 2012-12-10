
package com.moongate.bantatc;

import android.app.Activity;
import android.os.Bundle;
import android.view.View;

/**
 *
 * @author MoonGate
 */
public abstract class BaseReport extends Activity{
		public int report_type;
		
		public void onCreate(Bundle icicle, int content_view) {
			super.onCreate(icicle);
			setContentView(content_view);
		}		
		public void mostrar(View v){
			new wsReports().execute(this);
		}
		public abstract void mostrarReporte( wsReports.InstanciaReporte rep);
}
