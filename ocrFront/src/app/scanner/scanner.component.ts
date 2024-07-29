import { Component } from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {Observable, startWith, Subject, switchMap} from "rxjs";
import {Type} from "../category/category.component";
import {AsyncPipe, CommonModule, NgForOf, NgIf} from "@angular/common";
import {FormsModule} from "@angular/forms";
import {KeyValuePipe} from "../pipe/key-value.pipe";
import {NgxSpinnerComponent, NgxSpinnerModule, NgxSpinnerService} from "ngx-spinner";
import {BrowserModule} from "@angular/platform-browser";
import {BrowserAnimationsModule} from "@angular/platform-browser/animations";
import {ProgressSpinnerModule} from "primeng/progressspinner";
@Component({
  selector: 'app-scanner',
  standalone: true,
  imports: [
    CommonModule,
    AsyncPipe,
    FormsModule,
    KeyValuePipe,
    ProgressSpinnerModule,
  ],
  templateUrl: './scanner.component.html',
  styleUrl: './scanner.component.css'
})
export class ScannerComponent {

  image1: File | null = null;
  obj: any = {

  }

  types = new Subject<Observable<Type[]>>()
  types$ =this.types.pipe(startWith(this.getAllTypes()),switchMap((type)=>type));
  typeId: number = 0;
  onFileSelected(event: any) {

    this.image1 = event.target.files[0];
  }

  spinner1 = 'spinner1';
  loading=false;
  constructor(private http: HttpClient,private spinner: NgxSpinnerService) {

    this.spinner.show();
  }

  showSpinner(name: string) {
    this.spinner.show(name);
  }

  hideSpinner(name: string) {
    this.spinner.hide(name);
  }
  getAllTypes(): Observable<Type[]> {
    return this.http.get<Type[]>('http://localhost:8080/api/type/all');
  }
  submit(){
    if(this.image1) {
      this.loading = true
      const formData = new FormData();
      formData.append('image1', this.image1, this.image1.name);
      this.http.post(`http://localhost:5000/scan/${this.typeId}`, formData).subscribe((res) => {
         this.obj = res;
         this.loading = false;
        }
      )
    }
  }
}
