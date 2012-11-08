package com.moongate.bantatc;
import android.os.Bundle;
import android.app.Activity;
import android.content.Intent;
import android.view.Menu;
import android.view.View;
import android.widget.EditText;
import com.moongate.bantatc.R;

public class MainActivity extends Activity {
		private EditText eIP;
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
				eIP = (EditText) findViewById(R.id.editText);
				eIP.setText("192.168.1.99");
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.activity_main, menu);
        return true;
    }
    
    public void man_pro(View v) {
    	Intent mantenedorP = new Intent(MainActivity.this, mantenedor_pro.class);
			mantenedorP.putExtra("ip", eIP.getText().toString() );
    	startActivity(mantenedorP);
    }
    
    
}
