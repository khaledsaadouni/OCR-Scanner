package com.ocrService.ocrService.repository;

import com.ocrService.ocrService.modal.Label;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface LabelRepository extends JpaRepository<Label, Long>{
}
