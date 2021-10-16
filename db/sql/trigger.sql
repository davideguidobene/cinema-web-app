-- verifica che data di registrazione sia al più nel presente
CREATE TRIGGER registration_date_in_past
  BEFORE INSERT OR UPDATE OF registrationDate ON "User"
  FOR EACH ROW
BEGIN
  IF( :new.registrationDate > sysdate )
  THEN
    RAISE_APPLICATION_ERROR( -20001, 'Change date must be in the past' );
  END IF;
END;

-- verifica che data di registrazione sia successiva alla data di nascita
CREATE TRIGGER registration_date_after_birthdate
  BEFORE INSERT OR UPDATE ON "User"
  FOR EACH ROW
BEGIN
  IF( :new.registrationDate <= :new.birthdate)
  THEN
    RAISE_APPLICATION_ERROR( -20001, 'Change birthdate must be before registration date' );
  END IF;
END;

-- verifica che il numero di riga di un biglietto non superi il numero di righe presenti nel cinema
CREATE TRIGGER row_maximum_number
  BEFORE INSERT OR UPDATE OF "row" ON "Ticket"
  FOR EACH ROW
  WHEN :new.row <= (SELECT numberOfRows
                    FROM Room
                    WHERE :new.purchase==Purchase.id
                        AND Purchase.projection==Projection.id
                        AND Projection.room==Room.name)
  EXECUTE
    RAISE_APPLICATION_ERROR( -20001, 'Ticket row must be in the range of the Projection Room number of rows' );
END;

-- verifica che il numero di colonna di un biglietto non superi il numero di colonne presenti nel cinema
CREATE TRIGGER column_maximum_number
  BEFORE INSERT OR UPDATE OF "row" ON "Ticket"
  FOR EACH ROW
  WHEN :new.column <= (SELECT numberOfColumns
                    FROM Room
                    WHERE :new.purchase==Purchase.id
                        AND Purchase.projection==Projection.id
                        AND Projection.room==Room.name)
  EXECUTE
    RAISE_APPLICATION_ERROR( -20001, 'Ticket column must be in the range of the Projection Room number of columns' );
END;

-- verifica che la tripla (Ticket.row, Ticket.column, Ticket.Purchase.projection) sia unica
CREATE TRIGGER tripleUnique
  BEFORE INSERT OR UPDATE OF "row" ON "Ticket"
  FOR EACH ROW
  WHEN EXISTS (SELECT *
              FROM Ticket, Purchase
              WHERE Ticket.purchase==Purchase.id
                  AND Ticket.row==:new.row
                  AND Ticket.column==:new.column
                  AND Purchase.projection==(SELECT projection
                                            FROM Purchase
                                            WHERE Purchase.id==:new.projection))
  EXECUTE
    RAISE_APPLICATION_ERROR( -20001, 'Triple (Ticket.row, Ticket.column, Ticket.Purchase.projection) must be unique' );
END;

-- verifica che data di registrazione sia al più nel presente
CREATE TRIGGER purchase_datetime_in_past
  BEFORE INSERT OR UPDATE OF "purchaseDatetime" ON "Purchase"
  FOR EACH ROW
BEGIN
  IF( :new.purchaseDatetime > sysdate )
  THEN
    RAISE_APPLICATION_ERROR( -20001, 'Change date must be in the past' );
  END IF;
END;

-- verifica che data di acquisto sia antecedente alla data di proiezione
CREATE TRIGGER purchase_datetime_before_projection_datetime
  BEFORE INSERT OR UPDATE OF "purchaseDatetime" ON "Purchase"
  FOR EACH ROW
BEGIN
  WHEN :new.purchaseDatetime >  (SELECT datetime
                                FROM Projection
                                WHERE Projection.id==:new.projection) 
  EXECUTE
    RAISE_APPLICATION_ERROR( -20001, 'old projections cannot be purchased' );
END;

-- verifica che data di uscita di un film sia antecedente alla data di proiezione
CREATE TRIGGER movie_releasedate_before_projection_datetime
  BEFORE INSERT OR UPDATE OF "releaseDate" ON "Movie"
  FOR EACH ROW
BEGIN
  WHEN :new.releaseDate >  (SELECT datetime
                                FROM Projection
                                WHERE Projection.id==:new.projection) 
  EXECUTE
    RAISE_APPLICATION_ERROR( -20001, 'Projections cannot happen before the movie gets released' );
END;

CREATE TRIGGER projection_not_overlapping
  BEFORE INSERT OR UPDATE ON "Projection"
  FOR EACH ROW
BEGIN
  WHEN EXISTS (SELECT *
              FROM Projection
              WHERE Projection.id!=:new.id
                  AND Projection.room==:new.room
                  AND ((Projection.datetime<=:new.datetime
                  AND Projection.datetime+Projection.duration>=:new.datetime)
                  OR (Projection.datetime>=:new.datetime
                  AND Projection.datetime<=:new.datetime+Projection.duration)))
  EXECUTE
    RAISE_APPLICATION_ERROR( -20001, 'Projections should not overlap' );
END;



-- Nota: ai fini di mantenere la documentazione il più chiara e di facile lettura possibile non sono stati riportati alcuni trigger che derivano in modo banale da altri trigger già illustrati.
-- Per esempio per garantire che la tripla (Ticket.row, Ticket.column, Ticket.Purchase.projection) sia unica il trigger che si attiva in caso di insert o update su TIcket non basta e ne servirebbe uno analogo che agisse in caso di insert o update su Purchase
