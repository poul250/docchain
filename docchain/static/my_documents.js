$(document).ready(() => {
  // подписываем документ
  $(".sign").click((e) => {
    // получаем данные документа
    let doc = $(e.target).parents(".doc");
    let docId = doc.attr("docId");
    let myStatus = doc.attr("my_status");
    let signerStatus = doc.attr("signer_status");

    // если он уже подписан
    if (myStatus == 1) return false;

    // отправляем запрос на подписание
    $.get("sign/" + docId).done((data) => {
      // если произошла ошибка
      if (data.status != "ok") {
        alert("Произошла ошибка. Попробуйте позже или обратитесь в поддержку");
        return false;
      }
      // обновляем статус
      doc.attr("my_status", 1);
      // изменяем текст
      $(e).html("Вы подписали").addClass("text-succces");
    });
  });

  // открытие формы ввода email popap
  $(".sent_signer").click((e) => {
    // получаем данные документа
    let doc = $(e.target).parents(".doc");
    let docId = doc.attr("docId");
    let myStatus = doc.attr("my_status");
    let signerStatus = doc.attr("signer_status");

    // если он уже подписан
    if (signerStatus != 0) return false;

    // открываем модальное окно
    $("#exampleModal").modal("show");

    // записываем id документа
    $('[name="document_id"]').attr("value", docId);
  });

  // отправляем форму
  $("#sign_req").submit(function () {
    $.post(
      "/request_sign", // адрес обработчика
      $("#request_sign").serialize(), // отправляемые данные

      function (msg) {
        // закрываем окно
        $("#exampleModal").modal("hide");
        // обновляем статус
        alert($("#sign_req").serialize());
      },
    );

    return false;
  });
  ///// загрузка и отправка документов ///////
  $("#addDocBtn").click(() => {
    // вызываем выбор файла
    $("#document").click();

    // когда файл выбран
    $("#document").change(() => {
      // отправляем форму
      $("#formDoc").submit();
    });
  });

  // модальное окно
  $("#exampleModal").on("shown.bs.modal", function () {
    $("#signer_mail").trigger("focus");
  });
});
