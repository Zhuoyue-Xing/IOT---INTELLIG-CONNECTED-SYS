package com.example.iotlab5;

import androidx.appcompat.app.AppCompatActivity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.speech.RecognizerIntent;
//import android.support.v4.widget.SwipeRefreshLayout;
//import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;
import android.widget.EditText;
import android.widget.Button;
import android.os.AsyncTask;

import java.io.UnsupportedEncodingException;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Locale;

import com.loopj.android.http.*;

import org.json.*;

import cz.msebera.android.httpclient.Header;
import cz.msebera.android.httpclient.entity.StringEntity;
import cz.msebera.android.httpclient.message.BasicHeader;
import cz.msebera.android.httpclient.protocol.HTTP;


import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.URL;
import java.net.URLConnection;
import java.util.List;
import java.util.Map;



public class MainActivity extends AppCompatActivity {
    private final int REQ_CODE = 100;
    TextView textView;
    Button sendButton;
    EditText urlText;
    String command = new String();
    String urlPath = new String();
    String path = new String();


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        textView = findViewById(R.id.text);
        ImageView speak = findViewById(R.id.speak);
        speak.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
                intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                        RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
                intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault());
                intent.putExtra(RecognizerIntent.EXTRA_PROMPT, "Need to speak");
                try {
                    startActivityForResult(intent, REQ_CODE);
                } catch (ActivityNotFoundException a) {
                    Toast.makeText(getApplicationContext(),
                            "Sorry your device is not supported",
                            Toast.LENGTH_SHORT).show();
                }
            }
        });

        urlText = findViewById(R.id.edit);

        sendButton = findViewById(R.id.button);
        sendButton.setOnClickListener(new Button.OnClickListener() {
            @Override
            public void onClick(View v) {

                urlPath = urlText.getText().toString();
                path = "http://" + urlPath;

                if (command.indexOf("send tweets")!=-1) {
                    new Test().execute();
                    sendGet(path, command);

                } else if (command.compareTo("weather")==0) {
                    new Test().execute();
                    sendGet(path, command);

                } else {
                    System.out.println("log pos 2");
                    sendGet(path, command);
                }


            }
        });

    }
    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        switch (requestCode) {
            case REQ_CODE: {
                if (resultCode == RESULT_OK && null != data) {
                    ArrayList<String> result = data
                            .getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS);
                    textView.setText(result.get(0));
                    command = result.get(0);
//                  new Test().execute();
                }
                break;
            }
        }
    }
    public class Test extends AsyncTask<String, Void, String> {
        protected void onPreExecute(){}

        protected String doInBackground(String... arg0){

            if (command.indexOf("send tweets")!=-1) {
                System.out.println("log pos 1");
                String[] tweet = command.split("send tweets ");
                String twiSend = "X-THINGSPEAKAPIKEY=1BTGSRWSXO6AAINJ&api_key=1BTGSRWSXO6AAINJ&status=" + tweet[1];
                sendPost("https://api.thingspeak.com/apps/thingtweet/1/statuses/update", twiSend);

            } else if (command.compareTo("weather")==0) {
                String geoRes = sendPost("https://www.googleapis.com/geolocation/v1/geolocate?key=AIzaSyCIGgXSrXj0O3nbjN7sf15kskcOcZWwm9o","");
                String[] geoRes0 = geoRes.split(",");
                String[] geoRes1 = geoRes0[0].split(":");
                String[] geoRes2 = geoRes0[1].split(":");
                String lat = geoRes1[2].substring(1);
                String lng = geoRes2[1].substring(1,geoRes2[1].length()-4);
                String urlWeather = "https://api.openweathermap.org/data/2.5/weather?lat="+lat+"&lon="+lng+"&APPID=4d34fa16a400db838cd70c2f138dd831";
                String weatherRes = sendPost(urlWeather,"");

                try {
                    JSONObject jsonObject = new JSONObject(weatherRes);
//                    List<String> list = new ArrayList<String>();
                    JSONArray jsonArray = jsonObject.getJSONArray("weather");
                    String weatherMain = jsonArray.getJSONObject(0).getString("main");
                    double temp = Math.round((Double.parseDouble(jsonObject.getJSONObject("main").getString("temp")) - 273.15) * 100) / 100.0d;

                    String weatherTemp = weatherMain + " " + temp + " C";
                    System.out.println(weatherTemp);
                    command = command + " " + weatherTemp;

                } catch (JSONException e) {

                }

            } else {
                System.out.println("log pos 2");
            }

            return " ";
        }


    }

    private void sendGet(String path, String msg) {

        AsyncHttpClient client = new AsyncHttpClient();
//        RequestParams params = new RequestParams();
//        params.put("command", msg);


        JSONObject jsonParams = new JSONObject();
        try{
            jsonParams.put("Command", msg);
            try {
                StringEntity entity = new StringEntity(jsonParams.toString());
                client.post(this, path, entity, "application/json", new AsyncHttpResponseHandler() {
                    //        client.post(path, new AsyncHttpResponseHandler() {
                    @Override
                    public void onSuccess(int i, Header[] headers, byte[] responseBody) {
                        Toast.makeText(getApplicationContext(), "Get response from huzzah: " + responseBody.toString(), Toast.LENGTH_LONG).show();
                    }

                    @Override
                    public void onFailure(int i, Header[] headers, byte[] responseBody, Throwable throwable) {
                        Toast.makeText(getApplicationContext(), "Cannot not reach server: " + urlPath, Toast.LENGTH_LONG).show();
                    }
                });
            } catch (UnsupportedEncodingException e) {

            }
        } catch (JSONException e) {

        }



    }


    public static String sendPost(String url, String param) {
        PrintWriter out = null;
        BufferedReader in = null;
        String result = "";
        try {
            URL realUrl = new URL(url);

            URLConnection conn = realUrl.openConnection();

            conn.setRequestProperty("accept", "*/*");
            conn.setRequestProperty("connection", "Keep-Alive");
            conn.setRequestProperty("user-agent","Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1;SV1)");

            conn.setDoOutput(true);
            conn.setDoInput(true);

            out = new PrintWriter(conn.getOutputStream());

            out.print(param);

            out.flush();

            in = new BufferedReader(new InputStreamReader(conn.getInputStream()));
            String line;
            while ((line = in.readLine()) != null) {
                result += line;
            }
        } catch (Exception e) {
            System.out.println("POST Error!"+e);
            e.printStackTrace();
        }

        finally{
            try{
                if(out!=null){
                    out.close();
                }
                if(in!=null){
                    in.close();
                }
            }
            catch(IOException ex){
                ex.printStackTrace();
            }
        }
        System.out.println("post result:"+result);
        return result;
    }


}