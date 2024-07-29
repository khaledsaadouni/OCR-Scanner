package com.ocrService.ocrService.modal;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.ColumnDefault;

import java.util.List;

@Entity
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class Type {
    @Id
    @GeneratedValue
    private Long id;
    private String name;
    private String image;
    private double width;
    private double height;
    private int threshold;
    @ColumnDefault("0")
    private boolean crop;
    @OneToMany(mappedBy = "type",cascade = CascadeType.ALL)
    private List<Label> labels;
}
