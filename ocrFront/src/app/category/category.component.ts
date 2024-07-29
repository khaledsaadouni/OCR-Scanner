import { Component } from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {catchError, EMPTY, Observable, startWith, Subject, switchMap, tap} from "rxjs";
import {FormsModule} from "@angular/forms";
import {AsyncPipe, NgClass, NgForOf, NgIf} from "@angular/common";
import {RouterLink} from "@angular/router";
import {ProgressSpinnerModule} from "primeng/progressspinner";
export class Label{
  id: number=0;
  name: string='';
  top_x=0;
  top_y=0;
  bottom_x=0;
  bottom_y=0;
  threshold=0;

}
export class Type{
  id: number=0;
  name: string='';
  image: string='';
  crop: boolean=false;
  width=0;
  height=0;
  threshold=0;
  labels: Label[]=[];
}
@Component({
  selector: 'app-category',
  standalone: true,
  imports: [
    FormsModule,
    AsyncPipe,
    NgIf,
    NgForOf,
    RouterLink,
    ProgressSpinnerModule,
    NgClass
  ],
  templateUrl: './category.component.html',
  styleUrl: './category.component.css'
})

export class CategoryComponent {

  image1: File | null = null;


  uploadFile(file: File,id:number,width:number,height:number) {
    const formData = new FormData();
    formData.append('image1', file, file.name);
    return  this.http.post<{ message:string,path:string }>(`http://localhost:5000/uploadType/`+id, formData);
  }
  onFileSelected(event: any) {

    this.image1 = event.target.files[0];
  }

  types = new Subject<Observable<Type[]>>()
  types$ =this.types.pipe(startWith(this.getAllTypes()),switchMap((type)=>type));
  constructor(private http: HttpClient) {
  }
  type = new Type();
  loading= false;
  submit() {
    this.loading = true;
   this.createType(this.type).subscribe((data)=> {
     if(this.image1){
       this.uploadFile(this.image1,data.id,data.width,data.height).pipe(
         tap((d)=>console.log(d)),
         switchMap((d)=> {
           const type = new Type();
           type.id = data.id;
            type.image = d.path;
           return  this.setImage(type)
         }),
         catchError((err)=>{console.log(err);this.types.next(this.deleteType(data.id));return EMPTY}),
         tap(()=> {
           this.loading = false;
           this.types.next(this.getAllTypes())
         })).subscribe()
     }
   })
  }
  delete(id: number) {
    this.types.next(this.deleteType(id))
  }
  getAllTypes(): Observable<Type[]> {
    return this.http.get<Type[]>('http://localhost:8080/api/type/all');
  }
  createType(type: Type): Observable<Type> {
    return this.http.post<Type>('http://localhost:8080/api/type/create', type);
  }
  setImage(type: Type): Observable<Type> {
    return this.http.post<Type>(`http://localhost:8080/api/type/setImage`, type);
  }
  deleteType(id: number): Observable<Type[]> {
    return this.http.delete<Type[]>('http://localhost:8080/api/type/delete/' + id);
  }
  addCategory = false;
  add() {
    this.addCategory = !this.addCategory;
  }
}
