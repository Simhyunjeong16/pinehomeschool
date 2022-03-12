package com.example.user.myapplication;
import android.Manifest;
import android.app.AlertDialog;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.database.Cursor;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Bundle;
import android.provider.MediaStore;
import android.renderscript.Sampler;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;
import android.support.v4.app.ActivityCompat;
import android.support.v4.app.Fragment;
import android.support.v4.content.ContextCompat;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.Toast;

import com.microsoft.projectoxford.face.FaceServiceClient;
import com.microsoft.projectoxford.face.FaceServiceRestClient;
import com.microsoft.projectoxford.face.contract.Emotion;
import com.microsoft.projectoxford.face.contract.Face;

import static android.app.Activity.RESULT_OK;
import static com.example.user.myapplication.ImagePro.TAG;

import net.gotev.uploadservice.MultipartUploadRequest;
import net.gotev.uploadservice.UploadNotificationConfig;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.URLEncoder;
import java.util.Arrays;
import java.util.List;
import java.util.UUID;

public class Menu1Fragment extends Fragment {

    private ImagePro imagePro;
    private static final int MY_CAMERA_REQUEST_CODE = 100;
    private ImageView ivCrop;
    private ImagePro.ImageDetails imageDetails;

    //Image request code
    private static final int PICK_IMAGE_REQUEST = 22;

    //storage permission code
    private static final int STORAGE_PERMISSION_CODE = 2342;

    //Bitmap to get image from gallery
    private Bitmap bitmap;

    //Uri to store the image uri
    private Uri filePath;

    private static final String UPLOAD_URL = "http://203.252.208.222/upload.php";

    String a = null;
    String childname = null;

    private final String apiEndpoint = "https://koreacentral.api.cognitive.microsoft.com/face/v1.0/";
    private final String subscriptionKey = "24ca52a877b44258a1de47de06888a8a";
    private final FaceServiceClient faceServiceClient = new FaceServiceRestClient(apiEndpoint, subscriptionKey);
    private final int PICK_IMAGE = 1;
    String face_description_anger, face_description_surprise, face_description_happiness, face_description_sadness;

    @Override
    public void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        if (requestCode == ImagePro.CAMERA_CODE) {
            imageDetails = imagePro.getImagePath(ImagePro.CAMERA_CODE, RESULT_OK, data);
            Log.e("^^","requestCode"+requestCode);
            Log.d(" ### ", imageDetails.getPath() + ", " + imageDetails.getBitmap().getConfig());
            try {
                bitmap = MediaStore.Images.Media.getBitmap(getActivity().getContentResolver(),imageDetails.uri);
                detectAndFrame(bitmap);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
        else if (requestCode == ImagePro.GALLERY_CODE) {
            Log.d(" $$$ ","resultCode:"+resultCode);
            imageDetails = imagePro.getImagePath(ImagePro.GALLERY_CODE, RESULT_OK, data);
            try {
                bitmap = MediaStore.Images.Media.getBitmap(getActivity().getContentResolver(),imageDetails.uri);
                detectAndFrame(bitmap);
            } catch (IOException e) {
                e.printStackTrace();
            }

        }
        ivCrop.setImageBitmap(imageDetails.getBitmap());
    }

    private void detectAndFrame(final Bitmap imageBitmap) {
        ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
        imageBitmap.compress(Bitmap.CompressFormat.JPEG, 100, outputStream);
        ByteArrayInputStream inputStream = new ByteArrayInputStream(outputStream.toByteArray());

        AsyncTask<InputStream, String, Face[]> detectTask =
                new AsyncTask<InputStream, String, Face[]>() {

                    @Override
                    protected Face[] doInBackground(InputStream... params) {
                        try {

                            Face[] result = faceServiceClient.detect(
                                    params[0],
                                    false,         // returnFaceId
                                    true,        // returnFaceLandmarks// returnFaceAttributes:
                                    new FaceServiceClient.FaceAttributeType[] {
                                            FaceServiceClient.FaceAttributeType.Emotion }
                            );

                            List<Face> faces;
                            faces = Arrays.asList(result);

                            face_description_anger = String.format("%s", faces.get(0).faceAttributes.emotion.anger*100);
                            face_description_surprise = String.format("%s", faces.get(0).faceAttributes.emotion.surprise*100);
                            face_description_happiness = String.format("%s", faces.get(0).faceAttributes.emotion.happiness*100);
                            face_description_sadness = String.format("%s", faces.get(0).faceAttributes.emotion.sadness*100);

                            Log.d("########anger", face_description_anger);
                            Log.d("########surp", face_description_surprise);
                            Log.d("########happy", face_description_happiness);
                            Log.d("########sad", face_description_sadness);

                            return result;
                        } catch (Exception e) {
                            return null;
                        }
                    }

                    @Override
                    protected void onPreExecute() { }

                    @Override
                    protected void onProgressUpdate(String... progress) { }

                    @Override
                    protected void onPostExecute(Face[] result) {
                        if (result == null) return;
                    }
                };

        detectTask.execute(inputStream);
    }

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {

        View v =inflater.inflate(R.layout.fragment_menu1, container, false);

        ImageButton fab = (ImageButton) v.findViewById(R.id.add_photo);
        Button btn1 = (Button)v.findViewById(R.id.push_button1);
        Button btn2 = (Button)v.findViewById(R.id.push_button2);
        Button btn3 = (Button)v.findViewById(R.id.push_button3);
        Button btn4 = (Button)v.findViewById(R.id.push_button4);

        fab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if (ActivityCompat.checkSelfPermission(getContext(),Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
                    requestPermissions(new String[]{Manifest.permission.CAMERA}, MY_CAMERA_REQUEST_CODE);
                }
                imagePro.openImagePickOption();

            }
        });

        btn1.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                a= "happy";
                show();
            }
        });

        btn2.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                a= "angry";
                show();
            }
        });

        btn3.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                a= "surprise";
                show();
            }
        });

        btn4.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                a= "sad";
                show();
            }
        });

        imagePro = new ImagePro(this.getActivity());
        ivCrop = (ImageView) v.findViewById(R.id.user);

        return v;

    }

    public void show(){
        AlertDialog.Builder builder = new AlertDialog.Builder(getActivity());

        String tv_text = null;
        String emo = null;

        if (a =="happy"){
            tv_text = face_description_happiness;
            emo = "행복";
        }
        else if (a == "sad"){
            tv_text = face_description_sadness;
            emo = "슬픔";
        }
        else if (a =="surprise") {
            tv_text = face_description_surprise;
            emo = "놀라움";
        }
        else if(a =="angry"){
            tv_text = face_description_anger;
            emo = "화남";
        }

        if(tv_text == null){
            builder.setTitle("사진 선택 오류");
            //타이틀설정
            builder.setMessage("\n" + "얼굴이 나온 사진이 선택되지 않았습니다." + "\n" + "\n" + "되도록이면 정면 사진을 넣어주세요.");
            //내용설정
            builder.setPositiveButton("확인",
                    new DialogInterface.OnClickListener() {
                        public void onClick(DialogInterface dialog, int which) {
                        }
                    });
            builder.show();
        }

        else{
            builder.setTitle("감정 수치 확인");
            //타이틀설정
            builder.setMessage("사진 속 인물의 " + emo + "의 수치는 " + tv_text + "%입니다." + "\n" + "\n" + "이 사진으로 학습을 진행하시겠습니까?");
            //내용설정
            builder.setPositiveButton("확인",
                    new DialogInterface.OnClickListener() {
                        public void onClick(DialogInterface dialog, int which) {

                            AlertDialog.Builder ad = new AlertDialog.Builder(getActivity());
                            ad.setTitle("아이 이름 입력");       // 제목 설정
                            ad.setMessage("\n" + "\n" + "학습하는 동안 아이의 이름을 불러드립니다." + "\n" + "\n" + "입력을 안하시면 기본 설정인 '친구'로 설정됩니다.");   // 내용 설정

                            final EditText et = new EditText(getActivity());
                            ad.setView(et);

                            ad.setPositiveButton("확인", new DialogInterface.OnClickListener() {
                                @Override
                                public void onClick(DialogInterface dialog, int which) {
                                    childname = et.getText().toString();
                                    Toast.makeText(getContext(), "학습 준비 완료", Toast.LENGTH_LONG).show();
                                    uploadMultipart();
                                    dialog.dismiss();
                                }
                            });

                            ad.show();

                        }
                    });

            builder.setNegativeButton("취소",
                    new DialogInterface.OnClickListener() {
                        public void onClick(DialogInterface dialog, int which) {
                            //                        Toast.makeText(getContext(),"취소완료",Toast.LENGTH_LONG).show();
                        }
                    });
            builder.show();
        }
    }

    public void uploadMultipart() {

        //getting name for the image
        String name = a;
        String path =imageDetails.getPath();

        String emotion_value = null;
        if (a =="happy"){
            emotion_value = face_description_happiness;
        }
        else if (a == "sad"){
            emotion_value = face_description_sadness;
        }
        else if (a =="surprise") {
            emotion_value = face_description_surprise;
        }
        else if(a =="angry"){
            emotion_value =  face_description_anger;
        }

        Log.i("##3", String.valueOf(emotion_value));

        //Uploading code
        try {
            String uploadId = UUID.randomUUID().toString();

            //Creating a multi part request
            new MultipartUploadRequest (getContext(), uploadId, UPLOAD_URL)
                    .setUtf8Charset()
                    .addFileToUpload(path, "image") //Adding file (이미지 path넣기)
                    .addParameter("name", name) //Adding text parameter to the request
                    .addParameter("childname", childname) //Adding text parameter to the request
                    .addParameter("emotion_value", emotion_value) //Adding text parameter to the request
                    .setNotificationConfig(new UploadNotificationConfig())
                    .setMaxRetries(2)//최대 재시도 횟수
                    .startUpload(); //Starting the upload

        } catch (Exception exc) {
            Toast.makeText(getContext(), exc.getMessage(), Toast.LENGTH_SHORT).show();
        }
    }

}