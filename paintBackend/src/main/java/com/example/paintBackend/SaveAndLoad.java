package com.example.paintBackend;

import java.beans.XMLDecoder;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.beans.XMLEncoder;
import java.io.*;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

public class SaveAndLoad {

    public void saveInJson(String path) {
        ObjectMapper mapper = new ObjectMapper();
        StoreToSave storeToSave = new StoreToSave();
        try {
            String jsonFile = mapper.writeValueAsString(StoreToSave.store_hashmap);
            UndoAndRedo.clearUndo();
            UndoAndRedo.clearRedo();
            Iterator it = StoreToSave.store_hashmap.entrySet().iterator();
            while (it.hasNext()) {
                Map.Entry pair = (Map.Entry) it.next();
                UndoAndRedo.undo_hashmap.put((Long) pair.getKey(), (String[]) pair.getValue());
                it.remove();
            }
            storeToSave.clearHash();

            // Use the project's root directory to save the file
            String projectDir = System.getProperty("user.dir");
            File file = new File(projectDir, path);
            if (!file.exists()) {
                // Ensure parent directories exist
                file.getParentFile().mkdirs();
                // Attempt to create the file
                if (!file.createNewFile()) {
                    throw new IOException("Failed to create new file: " + path);
                }
            }

            try (FileWriter writer = new FileWriter(file)) {
                writer.write(jsonFile);
                writer.flush();
            }
        } catch (JsonProcessingException e) {
            System.err.println("Failed to process JSON: " + e.getMessage());
            e.printStackTrace();
        } catch (IOException e) {
            System.err.println("I/O error: " + e.getMessage());
            e.printStackTrace();
        } catch (Exception e) {
            System.err.println("Unexpected error: " + e.getMessage());
            e.printStackTrace();
        }
    }
    public void saveInXML(String path){
        StoreToSave storeToSave = new StoreToSave();
        try(FileOutputStream out = new FileOutputStream(new File(path).getAbsolutePath())){
            XMLEncoder encoder = new XMLEncoder(out);
            encoder.writeObject(StoreToSave.store_hashmap);
            UndoAndRedo.clearUndo();
            UndoAndRedo.clearRedo();
            Iterator it = StoreToSave.store_hashmap.entrySet().iterator();
            while (it.hasNext()) {
                Map.Entry pair = (Map.Entry)it.next();
                UndoAndRedo.undo_hashmap.put((Long) pair.getKey(), (String[]) pair.getValue());
                it.remove();
            }
            storeToSave.clearHash();

            encoder.close();
        } catch (FileNotFoundException e) {
            throw new RuntimeException(e);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    public HashMap<Long, String[]> loadFromXML(String path){
        HashMap<Long, String[]> loadMap = new HashMap<>();
        try(InputStream in = new FileInputStream(new File(path).getAbsolutePath())){
            XMLDecoder decoder = new XMLDecoder(in);
            loadMap = (HashMap<Long,String[]>)decoder.readObject();
            decoder.close();
        } catch (FileNotFoundException e) {
            throw new RuntimeException(e);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
        StoreToSave storeToSave = new StoreToSave();
        storeToSave.setStore_hashmap(loadMap);
        return loadMap;
    }
}