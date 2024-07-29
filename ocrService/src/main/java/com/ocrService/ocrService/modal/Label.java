package com.ocrService.ocrService.modal;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class Label {

    @Id
    @GeneratedValue
    private Long id;
    private String name;
    private double top_x;
    private double top_y;
    private double bottom_x;
    private double bottom_y;
    @ManyToOne()
    @JoinColumn(name = "type_id")
    private Type type;
}
