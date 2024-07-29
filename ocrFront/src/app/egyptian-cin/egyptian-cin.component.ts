import {Component, inject} from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {AsyncPipe, NgForOf, NgIf} from "@angular/common";

@Component({
  selector: 'app-egyptian-cin',
  standalone: true,
  imports: [
    AsyncPipe,
    NgForOf,
    NgIf
  ],
  templateUrl: './egyptian-cin.component.html',
  styleUrl: './egyptian-cin.component.css'
})
export class EgyptianCinComponent {
  title = 'ocrFront';
  http: HttpClient = inject(HttpClient);
  users$ = this.http.get<any[]>('http://localhost:8080/api/user/all');
  onFileSelected(event: any) {
    const file: File = event.target.files[0];
    this.uploadFile(file);
  }

  uploadFile(file: File) {
    const formData = new FormData();
    formData.append('file', file, file.name);
    this.http.post<any>('http://localhost:5000/upload', formData).subscribe();
  }
}
