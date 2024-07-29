import {Component, inject} from '@angular/core';
import {AsyncPipe, NgForOf, NgIf} from "@angular/common";
import {HttpClient} from "@angular/common/http";
import {Observable, startWith, Subject, switchMap} from "rxjs";

@Component({
  selector: 'app-tunisian-cin',
  standalone: true,
  imports: [
    AsyncPipe,
    NgForOf,
    NgIf
  ],
  templateUrl: './tunisian-cin.component.html',
  styleUrl: './tunisian-cin.component.css'
})
export class TunisianCinComponent {
  title = 'ocrFront';
  http: HttpClient = inject(HttpClient);
  users = new Subject<Observable<any>|null>();
  users$ = this.users.pipe(startWith(null), switchMap((obs) => obs??this.http.get<any[]>('http://localhost:8080/api/user/all')));
  onFileSelected(event: any) {
    const file: File = event.target.files[0];
    this.uploadFile(file);
  }

  uploadFile(file: File) {
    const formData = new FormData();
    formData.append('file', file, file.name);
    this.http.post<any>('http://localhost:5000/upload', formData).subscribe();
  }
  image1: File | null = null;
  image2: File | null = null;


  onFileChange(event: any, imageType: string) {
    const file = event.target.files[0];
    if (imageType === 'image1') {
      this.image1 = file;
    } else if (imageType === 'image2') {
      this.image2 = file;
    }
  }
  delete(id:number){
    this.users.next(  this.http.delete<any>('http://localhost:8080/api/user/delete/'+id))
  }

  onSubmit() {
    const formData = new FormData();
    if (this.image1) {
      formData.append('image1', this.image1);
    }
    if (this.image2) {
      formData.append('image2', this.image2);
    }

    this.http.post('http://localhost:5000/upload', formData).subscribe(response => {
      this.image1 = null;
      this.image2 = null;
      this.users.next(null)
    });
  }
  editable=false

  edit() {
    this.editable = !this.editable;
  }

  onSubmitPassport() {
    const formData = new FormData();
    if (this.image1) {
      formData.append('image1', this.image1);
    }

    this.http.post('http://localhost:5000/uploadPassport', formData).subscribe(response => {
      this.image1 = null;
      this.image2 = null;
      this.users.next(null)
    });

  }
}

